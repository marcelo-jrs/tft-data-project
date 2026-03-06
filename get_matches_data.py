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
checkpoint_folder = f"data/checkpoint/{base_date}_match_data"
os.makedirs(checkpoint_folder, exist_ok=True)
print(f"Saving checkpoints to: {checkpoint_folder}")

# %%

df = pd.read_csv("data/matches_kr_players20260305_1755.csv")

df.head()

# %%

print("Loading matches data...")
df_matches_id = pd.read_csv("data/matches_kr_players20260305_1755.csv")
match_ids = df_matches_id['match_id'].tolist()

print(f"Loaded {len(match_ids)} matches IDs")

# %%

BATCH_SIZE = 10
all_participants = []
all_traits = []
all_units = []
all_game_metadata = []

# %%

for batch_start in range(0, len(match_ids), BATCH_SIZE):
    batch = match_ids[batch_start:batch_start + BATCH_SIZE]
    batch_num = batch_start // BATCH_SIZE + 1
    total_batches = (len(match_ids) // BATCH_SIZE) + 1
    
    print(f"\nBatch {batch_num}/{total_batches}")
    
    # Process each match in the batch
    for match_id in batch:
        try:
            url = f"https://{REGION}.api.riotgames.com/tft/match/v1/matches/{match_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                match_data = response.json()
                
                tft_set = match_data['info']['tft_set_number']

                game_metadata = {
                    'match_id': match_id,
                    'game_version': match_data['info']['game_version'],
                    'game_datetime': match_data['info']['game_datetime'],
                    'game_length': match_data['info']['game_length'],
                    'tft_set': tft_set
                }
                all_game_metadata.append(game_metadata)

                if tft_set == 16:
                    for participant in match_data['info']['participants']:
                        # --- 1. MAIN PARTICIPANT DATA ---
                        participant_row = {
                            'match_id': match_id,
                            'puuid': participant['puuid'],
                            'placement': participant['placement'],
                            'level': participant['level'],
                            'gold_left': participant['gold_left'],
                            'last_round': participant['last_round'],
                            'total_damage_to_players': participant['total_damage_to_players'],
                            'players_eliminated': participant['players_eliminated']
                        }
                        all_participants.append(participant_row)
                        
                        # --- 2. TRAITS DATA (one row per trait per player) ---
                        for trait in participant['traits']:
                            trait_row = {
                                'match_id': match_id,
                                'puuid': participant['puuid'],
                                'trait_name': trait['name'],
                                'num_units': trait['num_units'],
                                'style': trait['style'],  # 1=Bronze,2=Silver,3=Gold,4=Prismatic
                                'tier_current': trait['tier_current'],
                                'tier_total': trait['tier_total']
                            }
                            all_traits.append(trait_row)
                        
                        # --- 3. UNITS DATA (one row per unit per player) ---
                        for unit in participant['units']:
                            unit_row = {
                                'match_id': match_id,
                                'puuid': participant['puuid'],
                                'character_id': unit['character_id'],
                                'tier': unit['tier'],
                                'rarity': unit['rarity'],
                                'items': ','.join(unit.get('itemNames', []))
                            }
                            all_units.append(unit_row)
                    
                    print(f"Match {match_id} processed")
                else:
                    print(f"Match {match_id} is Set {tft_set}, skipping")
            else:
                print(f"Match {match_id} error {response.status_code}")
                
        except Exception as e:
            print(f"Match {match_id} failed: {e}")
        
        time.sleep(0.2)

    # Save main participants data
    if all_participants:
        pd.DataFrame(all_participants).to_csv(
            f"{checkpoint_folder}/batch_{batch_num}_participants.csv", index=False
        )
    
    # Save traits data
    if all_traits:
        pd.DataFrame(all_traits).to_csv(
            f"{checkpoint_folder}/batch_{batch_num}_traits.csv", index=False
        )
    
    # Save units data
    if all_units:
        pd.DataFrame(all_units).to_csv(
            f"{checkpoint_folder}/batch_{batch_num}_units.csv", index=False
        )
    
    # Save game metadata
    if all_game_metadata:
        pd.DataFrame(all_game_metadata).to_csv(
            f"{checkpoint_folder}/batch_{batch_num}_game_metadata.csv", index=False
        )
    
    print(f"Saved checkpoint after batch {batch_num}")
    
    # Breather between batches
    if batch_num < total_batches:
        time.sleep(2)

# %%

os.makedirs("data/final", exist_ok=True)

if all_participants:
    pd.DataFrame(all_participants).to_csv(f"data/final/participants_{base_date}.csv", index=False)

if all_traits:
    pd.DataFrame(all_traits).to_csv(f"data/final/traits_{base_date}.csv", index=False)

if all_units:
    pd.DataFrame(all_units).to_csv(f"data/final/units_{base_date}.csv", index=False)

if all_game_metadata:
    pd.DataFrame(all_game_metadata).to_csv(f"data/final/game_metadata_{base_date}.csv", index=False)

print(f"\nALL DONE!")
print(f"Participants: {len(all_participants)} rows (players)")
print(f"Traits: {len(all_traits)} rows")
print(f"Units: {len(all_units)} rows")
print(f"Game metadata: {len(all_game_metadata)} rows")

# %%
