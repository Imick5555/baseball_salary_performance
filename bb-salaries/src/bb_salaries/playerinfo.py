import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import time


# ==========================
# CONFIG
# ==========================

URLS = [
    'https://www.baseball-reference.com/leagues/majors/2018-standard-batting.shtml',
    'https://www.baseball-reference.com/leagues/majors/2019-standard-batting.shtml',
    'https://www.baseball-reference.com/leagues/majors/2020-standard-batting.shtml',
    'https://www.baseball-reference.com/leagues/majors/2021-standard-batting.shtml',
    'https://www.baseball-reference.com/leagues/majors/2022-standard-batting.shtml',
    'https://www.baseball-reference.com/leagues/majors/2023-standard-batting.shtml',
    'https://www.baseball-reference.com/leagues/majors/2024-standard-batting.shtml',
    'https://www.baseball-reference.com/leagues/majors/2025-standard-batting.shtml',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

COLUMNS = [
    'Rk','Player','Age','Team','Lg','WAR','G','PA','AB','R','H','2B','3B','HR','RBI',
    'SB','CS','BB','SO','BA','OBP','SLG','OPS','OPS+','rOBA','Rbat+','TB','GIDP',
    'HBP','SH','SF','IBB','Pos','Awards'
]


# ==========================
# SCRAPING
# ==========================

def scrape_batting_data(urls):
    all_data = []

    for url in urls:
        year = int(re.search(r'/(\d{4})', url).group(1))
        print(f"\nScraping {year}...")

        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        div = soup.find('div', id='switcher_players_standard_batting')
        if not div:
            print("  Switcher div not found")
            continue

        table = div.find('table', id='players_standard_batting')
        if not table:
            print("  Table not found")
            continue

        tbody = table.find('tbody')
        if not tbody:
            print("  Tbody not found")
            continue

        seen = set()

        for row in tbody.find_all('tr'):
            if row.get('class') and 'thead' in row.get('class'):
                continue

            cells = row.find_all(['th', 'td'])
            if len(cells) < 25:
                continue

            player_cell = cells[1]
            player_name = player_cell.get_text(strip=True)
            team = cells[3].get_text(strip=True)

            if player_name in seen and team != 'TOT':
                continue

            if team == 'TOT' or player_name not in seen:
                seen.add(player_name)

                row_dict = {'Year': year}

                pos_map = {
                    0: 'Rk', 1: 'Player', 2: 'Age', 3: 'Team', 4: 'Lg',
                    5: 'WAR', 6: 'G', 7: 'PA', 8: 'AB', 9: 'R', 10: 'H',
                    11: '2B', 12: '3B', 13: 'HR', 14: 'RBI', 15: 'SB',
                    16: 'CS', 17: 'BB', 18: 'SO', 19: 'BA', 20: 'OBP',
                    21: 'SLG', 22: 'OPS', 23: 'OPS+', 24: 'rOBA',
                    25: 'Rbat+', 26: 'TB', 27: 'GIDP', 28: 'HBP',
                    29: 'SH', 30: 'SF', 31: 'IBB', 32: 'Pos', 33: 'Awards'
                }

                for idx, cell in enumerate(cells):
                    col_name = pos_map.get(idx)
                    if not col_name:
                        continue

                    if col_name == 'Player':
                        row_dict['Player'] = player_name
                        a = cell.find('a')
                        if a:
                            row_dict['Player_Link'] = (
                                'https://www.baseball-reference.com' + a['href']
                            )
                    else:
                        row_dict[col_name] = cell.get_text(strip=True)

                for col in COLUMNS:
                    row_dict.setdefault(col, '')

                all_data.append(row_dict)

        print(f"  {len(seen)} players scraped for {year}")
        time.sleep(1.2)

    return all_data


# ==========================
# CLEANING
# ==========================

def clean_batting_data(df):
    numeric_cols = [
        'Age','WAR','G','PA','AB','R','H','2B','3B','HR','RBI','SB','CS',
        'BB','SO','OPS+','TB','GIDP','HBP','SH','SF','IBB','Rbat+'
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df[~df['Player'].str.contains('MLB Average', case=False, na=False)]
    df = df[df['PA'] >= 100]

    def get_batting_hand(name):
        if name.endswith('*'):
            return 'both'
        elif name.endswith('#'):
            return 'left'
        elif name.endswith('?'):
            return 'unknown'
        return 'right'

    df['batting_hand'] = df['Player'].apply(get_batting_hand)
    df['Player'] = df['Player'].str.rstrip('*#?')

    df = df.drop(columns=['Awards'])
    df = df.sort_values(['Player', 'Year'])
    df = df.drop_duplicates(subset=['Player', 'Year'], keep='first')

    player_counts = df['Player'].value_counts()
    players_2plus = player_counts[player_counts >= 3].index
    df = df[df['Player'].isin(players_2plus)]

    return df.reset_index(drop=True)


# ==========================
# PIPELINE
# ==========================

def main():
    all_data = scrape_batting_data(URLS)

    df = pd.DataFrame(
        all_data,
        columns=['Year'] + COLUMNS + ['Player_Link']
    )

    mlb = clean_batting_data(df)

    mlb.to_csv('MLB_2018_2025_Cleaned.csv', index=False)
    print("\nSaved: MLB_2018_2025_Cleaned.csv")


# ==========================
# ENTRY POINT
# ==========================

if __name__ == "__main__":
    main()
