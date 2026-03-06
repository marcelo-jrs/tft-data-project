# %%

import os
from dotenv import load_dotenv
import requests
import pandas as pd
import time
from datetime import datetime

# %%

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
REGION = "asia"

headers = {
    "X-Riot-Token": RIOT_API_KEY
}

# %%

base_date = datetime.now().strftime('%Y%m%d_%H%M')
checkpoint_folder = f"data/checkpoint/{base_date}"
os.makedirs(checkpoint_folder, exist_ok=True)
print(f"📁 Saving checkpoints to: {checkpoint_folder}")

# %%

df = pd.read_csv("data/kr_challenger_20260305_1725.csv")

df.head()

# %%

print("Loading challenger data...")
df_challengers = pd.read_csv("data/kr_challenger_20260305_1725.csv")
puuids = df_challengers['puuid'].tolist()

print(f"Loaded {len(puuids)} Challenger players")

# %%

BATCH_SIZE = 10
all_matches = []

# %%

for batch_start in range(0, len(puuids), BATCH_SIZE):
    batch = puuids[batch_start:batch_start + BATCH_SIZE]
    batch_num = batch_start // BATCH_SIZE + 1
    total_batches = (len(puuids) // BATCH_SIZE) + 1
    
    print(f"\nBatch {batch_num}/{total_batches}")
    
    for puuid in batch:
        try:
            url = f"https://{REGION}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
            response = requests.get(url, headers=headers, params={"count": 50})
            
            if response.status_code == 200:
                match_ids = response.json()
                print(f"  ✅ Player got {len(match_ids)} matches")
                
                for match_id in match_ids:
                    all_matches.append({
                        'puuid': puuid,
                        'match_id': match_id,
                        'batch': batch_num,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
            else:
                print(f"Player error {response.status_code}")
                
        except Exception as e:
            print(f"Player failed: {e}")
        
        time.sleep(0.2)
    
    checkpoint_file = f"{checkpoint_folder}/batch_{batch_num}_checkpoint.csv"
    temp_df = pd.DataFrame(all_matches)
    temp_df.to_csv(checkpoint_file, index=False)
    print(f"Saved: {checkpoint_file}")
    
    if batch_num < total_batches:
        print("  ⏳ 2 second breather...")
        time.sleep(2)


# %%

final_df = pd.DataFrame(all_matches)

final_date_file = f"data/matches_kr_players{base_date}.csv"
final_df.to_csv(final_date_file, index=False)


# %%
