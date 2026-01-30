import pandas as pd
import time
from data_extraction import TFTDataExtractor

extractor = TFTDataExtractor()
df_players = pd.read_csv('top_tft_players_kr.csv')

match_data = []
for player in df_players.itertuples():
    puuid = player.puuid
    try:
        match_history = extractor.get_match_history(puuid, region='asia', count=20)
        for match_id in match_history:
            match_data.append({'puuid': puuid, 'match_id': match_id})
    except Exception as e:
        if "429" in str(e):
            print(f"Rate limit exceeded: {e}")
            break
        else:
            print(f"Failed to get match history for PUUID {puuid}: {e}")
            continue

df_matches = pd.DataFrame(match_data)
df_matches.to_csv('data/match_ids.csv', index=False)
print(f"Match IDs saved to match_ids.csv ({len(match_data)} total matches)")


