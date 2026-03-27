import os
import csv
import urllib.request

# ── 1. DESCARGA DE DATOS BRUTOS ───────────────────────────────────────────────
CSV_URL = "https://raw.githubusercontent.com/salimt/football-datasets/main/datalake/transfermarkt/player_profiles/player_profiles.csv"
LOCAL_CSV = "tm_player_profiles.csv"

if not os.path.exists(LOCAL_CSV):
    print("Descargando dataset...")
    urllib.request.urlretrieve(CSV_URL, LOCAL_CSV)
    print("Descarga completada.")

# Mapeo de clubes
leagues_info = {
    'LaLiga': {
        'country': 'Spain',
        'clubs': ['Real Madrid', 'FC Barcelona', 'Atlético de Madrid', 'Athletic Bilbao', 'Real Sociedad']
    },
    'Premier League': {
        'country': 'England',
        'clubs': ['Arsenal FC', 'Manchester City', 'Liverpool FC', 'Chelsea FC', 'Tottenham Hotspur']
    },
    'Bundesliga': {
        'country': 'Germany',
        'clubs': ['Bayern Munich', 'Borussia Dortmund', 'Bayer 04 Leverkusen', 'Eintracht Frankfurt', 'RB Leipzig']
    },
    'Serie A': {
        'country': 'Italy',
        'clubs': ['Inter Milan', 'Juventus FC', 'SSC Napoli', 'AC Milan', 'Atalanta BC']
    },
    'Ligue 1': {
        'country': 'France',
        'clubs': ['Paris Saint-Germain', 'Olympique Marseille', 'AS Monaco', 'Strasbourg', 'OGC Nice']
    }
}

# Diccionario invertido para buscar liga/país de cada club
club_to_league_info = {}
for league_name, info in leagues_info.items():
    for club in info['clubs']:
        club_to_league_info[club] = {'league': league_name, 'country': info['country']}

# Inicializar contadores por club
club_stats = {}
for club in club_to_league_info.keys():
    club_stats[club] = {'total': 0, 'local': 0, 'foreign': 0}

# ── 3. PREPROCESAMIENTO Y CRUCE DE DATOS ──────────────────────────────────────
print("Procesando datos de jugadores...")
with open(LOCAL_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        club = row.get('current_club_name', '').strip()
        citizenship = row.get('citizenship', '').strip()
        
        # Correcciones de nombres para hacer match con el dataset
        if club == 'Borussia Dortmund': club = 'BVB Dortmund'
        if club == 'Bayer 04 Leverkusen': club = 'Bayer Leverkusen'
        if club == 'Tottenham Hotspur': club = 'Tottenham'
        if club == 'Paris Saint-Germain': club = 'PSG'
        if club == 'Olympique Marseille': club = 'OL Marseille'
        
        if club in club_stats:
            # Determinamos si es local o extranjero
            league_country = club_to_league_info[club]['country']
            is_local = league_country in citizenship
            
            club_stats[club]['total'] += 1
            if is_local:
                club_stats[club]['local'] += 1
            else:
                club_stats[club]['foreign'] += 1

# ── 4. EXPORTACIÓN DEL DATASET UNIFICADO ──────────────────────────────────────
output_file = 'datos_localismo_ligas_europeas.csv'
print(f"Generando dataset final: {output_file}")

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'league_name', 'club_name', 'club_country', 'season',
        'total_players', 'local_players', 'foreign_players', 
        'local_ratio', 'foreign_ratio'
    ])
    
    # Rellenamos los datos preprocesados
    for club, stats in club_stats.items():
        if stats['total'] > 0:
            league = club_to_league_info[club]['league']
            country = club_to_league_info[club]['country']
            
            total = stats['total']
            local = stats['local']
            foreign = stats['foreign']
            local_ratio = round(local / total, 4)
            foreign_ratio = round(foreign / total, 4)
            
            writer.writerow([
                league, club, country, 2025,
                total, local, foreign, local_ratio, foreign_ratio
            ])

print("Preprocesamiento finalizado con éxito.")
