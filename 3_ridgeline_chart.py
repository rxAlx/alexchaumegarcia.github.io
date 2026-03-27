"""
Ridgeline Chart - Distribución de edades por liga
"""
import base64
import csv
import io
import os
import urllib.request
import re
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# ── 1. CARGA Y PREPROCESAMIENTO ───────────────────────────────────────────────
CSV_URL = "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/player_profiles/player_profiles.csv"
LOCAL_CSV = "tm_player_profiles.csv"

# Diccionario de equipos por liga
league_keywords = {
    'LaLiga': ['Real Madrid', 'Barcelona', 'Athletic', 'Real Sociedad', 'Sevilla', 'Betis'],
    'Serie A': ['Juventus', 'Inter', 'Milan', 'Napoli', 'Roma', 'Lazio', 'Atalanta'],
    'Premier League': ['Arsenal', 'Manchester', 'Liverpool', 'Chelsea', 'Tottenham', 'Newcastle'],
    'Bundesliga': ['Bayern Munich', 'Bayern München', 'Dortmund', 'Leverkusen', 'Leipzig', 'Frankfurt', 'Stuttgart'],
    'Ligue 1': ['Paris Saint-Germain', 'Paris SG', 'Marseille', 'Monaco', 'Lyon', 'Lille', 'Nice', 'Lens']
}

def get_league(club_name):
    club_name_lower = club_name.lower()
    for league, keywords in league_keywords.items():
        for kw in keywords:
            if kw.lower() in club_name_lower:
                return league
    return None

if not os.path.exists(LOCAL_CSV):
    print("Descargando dataset...")
    urllib.request.urlretrieve(CSV_URL, LOCAL_CSV)
    print("Descarga completada.")

league_ages = {l: [] for l in league_keywords.keys()}
current_year = 2025

# Leer datos y calcular edades
with open(LOCAL_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        club = row.get('current_club_name', '')
        dob = row.get('date_of_birth', '')
        league = get_league(club)
        
        if league and dob:
            try:
                birth_year = int(dob.split('-')[0])
                age = current_year - birth_year
                if 16 <= age <= 42:
                    league_ages[league].append(age)
            except ValueError:
                pass


# ── 2. CREACIÓN DEL GRÁFICO ───────────────────────────────────────────────────
# Filtramos ligas vacías y ordenamos por edad media
league_means = {l: np.mean(ages) for l, ages in league_ages.items() if len(ages) > 10}
leagues = sorted(league_means.keys(), key=lambda l: league_means[l], reverse=True)

# Colores por liga
LEAGUE_COLORS = {
    'Serie A':        '#F9E79F', # Amarillo pastel
    'LaLiga':         '#A8DADC', # Azul pastel
    'Premier League': '#FFB5A7', # Rojo/coral pastel
    'Bundesliga':     '#94D2BD', # Verde pastel
    'Ligue 1':        '#CDB4DB', # Violeta pastel
}

fig, ax = plt.subplots(figsize=(8.5, 5))
fig.patch.set_facecolor('#fafafa')
ax.set_facecolor('#fafafa')

x_eval = np.linspace(15, 45, 300)
spacing = 0.030

for i, league in enumerate(leagues):
    ages = league_ages[league]
    
    # Calcular Densidad Kernel (KDE)
    kde = gaussian_kde(ages, bw_method=0.18)
    y_dens = kde.evaluate(x_eval)
    
    # Escalar densidad y desplazar
    y_dens = y_dens / np.max(y_dens) * 0.045
    y_offset = (len(leagues) - 1 - i) * spacing
    y_plot = y_dens + y_offset

    color = LEAGUE_COLORS.get(league, '#aaaaaa')

    # Relleno y borde
    ax.fill_between(x_eval, y_offset, y_plot, color=color, alpha=0.75)
    ax.plot(x_eval, y_plot, color=color, linewidth=1.5)
    
    # Línea base para cada liga
    ax.plot([15, 45], [y_offset, y_offset], color='black', linewidth=0.5, alpha=0.3)
    
    # Textos: Nombre de liga (izquierda)
    ax.text(14, y_offset + 0.005, league, ha='right', va='bottom', 
            fontsize=8.5, fontweight='bold', color='#333333')

# ── 3. FORMATO DE EJES Y EXPORTACIÓN ──────────────────────────────────────────
ax.set_xlim(12, 45)
ax.set_ylim(-0.01, len(leagues) * spacing + 0.05)

ax.set_xticks([16, 20, 24, 28, 32, 36, 40])
ax.set_xticklabels(['16', '20', '24', '28', '32', '36', '40 años'], fontsize=8.5)
ax.set_xlabel('Edad del jugador', fontsize=9.5, color='#333333', fontweight='bold')
ax.tick_params(axis='x', colors='#333333')

ax.set_title(
    'Distribución de Edades en las Principales Ligas Europeas',
    fontsize=11.5, fontweight='bold', pad=15, color='#222222'
)

ax.set_yticks([])
ax.spines[['left', 'top', 'right']].set_visible(False)
ax.spines['bottom'].set_alpha(0.3)
ax.grid(axis='x', linestyle='--', alpha=0.35)

plt.tight_layout(rect=[0, 0.04, 1, 1])
fig.text(0.5, 0.01,
         'Fuente: https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/player_profiles/player_profiles.csv',
         ha='center', fontsize=6, color='gray', style='italic')

buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
buf.seek(0)
img_b64 = base64.b64encode(buf.read()).decode()
plt.close(fig)

html = f"""<!DOCTYPE html>
<html lang="es">
<body>
  <img src="data:image/png;base64,{img_b64}" alt="Gráfico ridgeline de distribución de edades por liga">
</body>
</html>"""

with open('ridgeline_chart.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("ridgeline_chart.html creado")
