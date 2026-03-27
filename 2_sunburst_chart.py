"""
Sunburst Chart - Jugadores Locales vs Extranjeros por Liga y Club (2025).
"""
import base64
import csv
import io
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

# ── Datos ──
DATA_FILE = 'datos_localismo_ligas_europeas.csv'

rows = []
with open(DATA_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Agrupar por liga manteniendo el orden del CSV
league_order = []
league_data  = defaultdict(lambda: {'clubs': []})
for row in rows:
    league = row['league_name']
    if league not in league_order:
        league_order.append(league)
    league_data[league]['clubs'].append({
        'name':    row['club_name'],
        'local':   int(row['local_players']),
        'foreign': int(row['foreign_players']),
        'total':   int(row['total_players']),
    })

leagues = sorted(league_order)

# ── Colores ──
LEAGUE_COLORS = {
    'Bundesliga':     '#94D2BD', # Verde pastel
    'LaLiga':         '#A8DADC', # Azul pastel
    'Ligue 1':        '#CDB4DB', # Violeta pastel
    'Premier League': '#FFB5A7', # Rojo/coral pastel
    'Serie A':        '#F9E79F', # Amarillo pastel
}
LOCAL_COLOR   = '#B4E197'  # Verde menta pastel
FOREIGN_COLOR = '#FAD7A1'  # Naranja pastel

def lighten(hex_color, factor=0.15):
    """Mezcla el color con blanco (factor=0 → original, factor=1 → blanco)."""
    h = hex_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    lighter = tuple(int(c + (255 - c) * factor) for c in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*lighter)

# ── Construir sectores de cada anillo ──
# Anillo 1 (interior): ligas
inner_sizes  = []
inner_colors = []
for l in leagues:
    inner_sizes.append(sum(c['total'] for c in league_data[l]['clubs']))
    inner_colors.append(LEAGUE_COLORS.get(l, '#888'))

# Anillo 2 (medio): clubs  – mismo orden que ligas, color más claro
mid_sizes  = []
mid_colors = []
mid_labels = []
for l in leagues:
    for club in league_data[l]['clubs']:
        mid_sizes.append(club['total'])
        mid_colors.append(lighten(LEAGUE_COLORS.get(l, '#888')))
        mid_labels.append(club['name'])

# Anillo 3 (exterior): local / extranjero por club
outer_sizes  = []
outer_colors = []
outer_meta   = []
for l in leagues:
    for club in league_data[l]['clubs']:
        club_total = club['local'] + club['foreign']
        outer_sizes.append(club['local'])
        outer_colors.append(LOCAL_COLOR)
        outer_meta.append({'count': club['local'], 'total': club_total})

        outer_sizes.append(club['foreign'])
        outer_colors.append(FOREIGN_COLOR)
        outer_meta.append({'count': club['foreign'], 'total': club_total})

# ── Figura ──
fig, ax = plt.subplots(figsize=(11, 8))
fig.patch.set_facecolor('#fafafa')

RING_W    = 0.20        # grosor de cada anillo
START_ANG = 90
CC_LOCK   = False       # sentido horario

# Anillo 1: ligas  (radio 0.40 → 0.60)
wedges_in, _ = ax.pie(
    inner_sizes, radius=0.60,
    colors=inner_colors,
    startangle=START_ANG, counterclock=CC_LOCK,
    wedgeprops=dict(width=RING_W, edgecolor='white', linewidth=1.8),
    labels=None,
)

# Anillo 2: clubs  (radio 0.60 → 0.80)
wedges_mid, _ = ax.pie(
    mid_sizes, radius=0.80,
    colors=mid_colors,
    startangle=START_ANG, counterclock=CC_LOCK,
    wedgeprops=dict(width=RING_W, edgecolor='white', linewidth=1.0),
    labels=None,
)

# Anillo 3: local/extranjero  (radio 0.80 → 1.00)
wedges_out, _ = ax.pie(
    outer_sizes, radius=1.00,
    colors=outer_colors,
    startangle=START_ANG, counterclock=CC_LOCK,
    wedgeprops=dict(width=RING_W, edgecolor='white', linewidth=0.8),
    labels=None,
)

# ── Etiquetas anillo 1: nombre liga + % del total ──────────────────────────────
grand_total = sum(inner_sizes)
for wedge, label, size in zip(wedges_in, leagues, inner_sizes):
    arc = abs(wedge.theta2 - wedge.theta1)
    if arc < 10:
        continue
    angle = (wedge.theta1 + wedge.theta2) / 2
    rad   = np.deg2rad(angle)
    r_mid = 0.60 - RING_W / 2          # punto medio del anillo 1
    x, y  = r_mid * np.cos(rad), r_mid * np.sin(rad)
    pct   = size / grand_total * 100
    short = (label.replace('Premier League', 'Premier')
                  .replace('Bundesliga', 'BL'))
    ax.text(x, y, f'{short}\n{pct:.0f}%',
            ha='center', va='center', fontsize=6.5,
            fontweight='bold', color='#333333')

# ── Etiquetas anillo 2: nombre del club + % dentro de la liga ────────────────
# Pre-calcular el total de cada liga para obtener el % del club
league_totals = {l: sum(c['total'] for c in league_data[l]['clubs']) for l in leagues}

# Metadatos de cada wedge del anillo medio (mismo orden que mid_sizes)
mid_meta = []
for l in leagues:
    for club in league_data[l]['clubs']:
        mid_meta.append({'club': club, 'league': l})

for wedge, meta in zip(wedges_mid, mid_meta):
    arc = abs(wedge.theta2 - wedge.theta1)
    if arc < 8:
        continue
    angle = (wedge.theta1 + wedge.theta2) / 2
    rad   = np.deg2rad(angle)
    r_mid = 0.80 - RING_W / 2
    x, y  = r_mid * np.cos(rad), r_mid * np.sin(rad)
    club   = meta['club']
    league = meta['league']
    lt     = league_totals[league]
    pct    = club['total'] / lt * 100 if lt > 0 else 0
    short  = club['name'] if len(club['name']) <= 8 else club['name'][:7] + '.'
    ax.text(x, y, f"{short}\n{pct:.0f}%",
            ha='center', va='center', fontsize=5.0,
            color='#333333', fontweight='bold')

# ── Etiquetas anillo 3: % local o % extranjero ────────────────────────────────
for wedge, meta in zip(wedges_out, outer_meta):
    if meta['total'] == 0:
        continue
    arc = abs(wedge.theta2 - wedge.theta1)
    if arc < 7:
        continue
    pct   = meta['count'] / meta['total'] * 100
    angle = (wedge.theta1 + wedge.theta2) / 2
    rad   = np.deg2rad(angle)
    r_mid = 1.00 - RING_W / 2          # punto medio del anillo 3
    x, y  = r_mid * np.cos(rad), r_mid * np.sin(rad)
    ax.text(x, y, f'{pct:.0f}%',
            ha='center', va='center', fontsize=5.5,
            color='#333333', fontweight='bold')

# ── Título y leyenda ──────────────────────────────────────────────────────────
ax.set_title(
    'Jugadores locales vs extranjeros\npor liga y club (temporada 2024-2025)',
    fontsize=11, fontweight='bold', pad=14
)

# ── Leyendas (2 separadas) ──────────────────────────────────────────────────
# 1. Leyenda de Ligas
legend_leagues = [
    mpatches.Patch(color=LEAGUE_COLORS['Bundesliga'],     label='Bundesliga'),
    mpatches.Patch(color=LEAGUE_COLORS['LaLiga'],         label='LaLiga'),
    mpatches.Patch(color=LEAGUE_COLORS['Ligue 1'],        label='Ligue 1'),
    mpatches.Patch(color=LEAGUE_COLORS['Premier League'], label='Premier League'),
    mpatches.Patch(color=LEAGUE_COLORS['Serie A'],        label='Serie A'),
]
leg_ligas = ax.legend(handles=legend_leagues, loc='center left',
                      bbox_to_anchor=(1.02, 0.70), ncol=1, fontsize=9, framealpha=0.92,
                      title='Ligas Europeas', title_fontsize=10)
ax.add_artist(leg_ligas)

# 2. Leyenda de Procedencia
legend_players = [
    mpatches.Patch(color=LOCAL_COLOR,                     label='Jugador Local'),
    mpatches.Patch(color=FOREIGN_COLOR,                   label='Jugador Extranjero'),
]
ax.legend(handles=legend_players, loc='center left',
          bbox_to_anchor=(1.02, 0.35), ncol=1, fontsize=9, framealpha=0.92,
          title='Procedencia', title_fontsize=10)

plt.tight_layout(rect=[0, 0.04, 1, 1])  # espacio para la fuente en la base
fig.text(0.5, 0.01,
         'Fuente: Transfermarkt Datasets - Github: salimt/football-datasets',
         ha='center', fontsize=6, color='gray', style='italic')

# ── Exportar HTML ─────────────────────────────────────────────────────────────
buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
buf.seek(0)
img_b64 = base64.b64encode(buf.read()).decode()
plt.close(fig)

html = f"""<!DOCTYPE html>
<html lang="es">

<body>
  <img src="data:image/png;base64,{img_b64}" alt="Gráfico sunburst de localismo en ligas europeas">
</body>
</html>"""

with open('sunburst_chart.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("sunburst_chart.html creado")
