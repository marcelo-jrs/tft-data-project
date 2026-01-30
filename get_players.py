import pandas as pd
from data_extraction import TFTDataExtractor

extractor = TFTDataExtractor()
try:
    top_players = extractor.get_top_players_data('kr')
    df_players = pd.DataFrame(top_players)
    df_players.to_csv('data/top_tft_players_kr.csv', index=False)
    print("Finished extracting top TFT players")
except Exception as e:
    print(f"Failed to extract players data: {e}")
