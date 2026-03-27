"""
Pyramid Chart - Deportistas Federados por Comunidad Autónoma (2024)
"""
import base64
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ── Datos ──
df = pd.read_csv('deportistas_federados_pyramid_chart.csv', sep=';')

df_filtered = df[
    (df['Sexo'].isin(['Hombres', 'Mujeres'])) &
    (df['periodo'] == 2024) &
    (df['Federación'] == 'TOTAL')
].copy()

df_filtered['Total_clean'] = (
    df_filtered['Total'].str.replace('.', '', regex=False).astype(int)
)

df_regions = df_filtered[df_filtered['Comunidad autónoma'] != 'TOTAL'].copy()

df_pivot = df_regions.pivot_table(
    index='Comunidad autónoma',
    columns='Sexo',
    values='Total_clean',
    aggfunc='sum'
).fillna(0)

df_pivot['Total'] = df_pivot['Hombres'] + df_pivot['Mujeres']
df_pivot = df_pivot.sort_values('Total', ascending=True).drop('Total', axis=1)

regions = df_pivot.index.tolist()
males   = df_pivot['Hombres'].values
females = df_pivot['Mujeres'].values

# ── Gráfico ──
fig, ax = plt.subplots(figsize=(9, 7.5))
fig.patch.set_facecolor('#f9f9f9')
ax.set_facecolor('#f9f9f9')

y = np.arange(len(regions))
BAR_H = 0.62

ax.barh(y, -males,   color='#1f77b4', label='Hombres', height=BAR_H)
ax.barh(y,  females, color='#ff7f0e', label='Mujeres',  height=BAR_H)

max_val = max(males.max(), females.max())
ax.set_xlim(-max_val * 1.30, max_val * 1.30)  # extra space for labels

# ── Etiquetas de valor ──
LABEL_FS  = 6.5
PADDING   = max_val * 0.015

for i, (m, f) in enumerate(zip(males, females)):
    # — Hombres: etiqueta a la izquierda del extremo de la barra —
    ax.text(-m - PADDING, i, f'{int(m):,}',
            ha='right', va='center', fontsize=LABEL_FS,
            color='#1f77b4')

    # — Mujeres: etiqueta a la derecha del extremo de la barra —
    ax.text(f + PADDING, i, f'{int(f):,}',
            ha='left', va='center', fontsize=LABEL_FS,
            color='#ff7f0e')

# ── Ejes y formato ────────────────────────────────────────────────────────────
xticks = ax.get_xticks()
ax.set_xticks(xticks)
ax.set_xticklabels([f'{abs(int(v)):,}' for v in xticks], fontsize=7.5)

ax.set_yticks(y)
ax.set_yticklabels(regions, fontsize=8)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('Número de deportistas', fontsize=10)
ax.set_title(
    'Deportistas federados por Comunidad Autónoma y Género (2024)',
    fontsize=12, fontweight='bold', pad=12
)

ax.legend(
    handles=[
        mpatches.Patch(color='#1f77b4', label='Hombres'),
        mpatches.Patch(color='#ff7f0e', label='Mujeres'),
    ],
    loc='lower right', fontsize=9, framealpha=0.8
)

ax.grid(axis='x', linestyle='--', alpha=0.35)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout(rect=[0, 0.04, 1, 1])  # espacio inferior para la fuente
fig.text(0.5, 0.01,
         'Fuente: https://datos.gob.es/es/catalogo/e05230301-licencias-federadas-por-federacion-periodo-sexo-y-comunidad-autonoma',
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
  <img src="data:image/png;base64,{img_b64}" alt="Gráfico de pirámide de deportistas federados">
</body>
</html>"""

with open('pyramid_chart.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("pyramid_chart.html creado")
