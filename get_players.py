# %%

from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
import requests

# %%

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
REGION = "kr"

headers = {
    "X-Riot-Token": RIOT_API_KEY
}


# %%

print("Fetching KR Challenger players...")
url = f"https://{REGION}.api.riotgames.com/tft/league/v1/challenger"
response = requests.get(url, headers=headers)

response

# %%

if response.status_code == 200:
    data = response.json()
    players = data['entries']

    print(f"Found {len(players)} Challenger players")

    players.sort(key=lambda x: x['leaguePoints'], reverse=True)
        
else:
    print(f"Error {response.status_code}: {response.text}")


# %%

df = pd.DataFrame(players)
    
df['region'] = REGION
df['tier'] = 'CHALLENGER'
df['collection_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

column_order = [
    'puuid', 
    'leaguePoints', 
    'rank', 
    'wins', 
    'losses', 
    'tier', 
    'region', 
    'collection_date',
    'veteran',
    'inactive',
    'freshBlood',
    'hotStreak',
]

available_columns = [col for col in column_order if col in df.columns]
df = df[available_columns]


# %%

df.head()

# %%

filename = f"data/kr_challenger_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
df.to_csv(filename, index=False, encoding='utf-8-sig')

print(f"Data saved to: {filename}")
print(f"File size: {len(df)} rows, {len(df.columns)} columns")

# %%

print("\n📊 Data Preview (Top 10 players):")
print("-" * 80)
print(df[['leaguePoints', 'wins', 'losses']].head(10).to_string(index=False))

print("\n📈 Summary Statistics:")
print(f"   Average LP: {df['leaguePoints'].mean():.0f}")
print(f"   Total wins across all players: {df['wins'].sum()}")
print(f"   Win Rate (avg): {(df['wins']/(df['wins']+df['losses'])).mean()*100:.1f}%")

# %%
