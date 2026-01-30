import os
import dotenv
import requests
import pandas as pd
import time

dotenv.load_dotenv()

class TFTDataExtractor:
    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY")
        if not self.api_key:
            raise ValueError("RIOT_API_KEY not found")
        self.request_times = []

    def _check_rate_limit(self):
        """Check and enforce rate limits: 20 requests/second, 100 requests/2 minutes."""
        current_time = time.time()
        self.request_times = [t for t in self.request_times if current_time - t < 120]
        
        # Check 100 requests per 2 minutes limit
        if len(self.request_times) >= 100:
            sleep_time = 120 - (current_time - self.request_times[0])
            if sleep_time > 0:
                print(f"Rate limit (100/2min) reached. Waiting {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
                self.request_times = []
        
        # Check 20 requests per second limit
        requests_this_second = len([t for t in self.request_times if current_time - t < 1])
        if requests_this_second >= 20:
            print("Rate limit (20/sec) reached. Waiting 0.05 seconds...")
            time.sleep(0.05)

    def get_top_players_data(self, region):
        url = f"https://{region}.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT"
        headers = {"X-Riot-Token": self.api_key}

        try:
            self._check_rate_limit()
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.request_times.append(time.time())
            league_data = response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch Challenger data: {e}")
        
        players = []
        
        for entry in league_data['entries']:
            puuid = entry['puuid']
            players.append({'puuid': puuid})
        
        return players
    
    def get_match_history(self, puuid, region="asia", count=20):
        url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"
        headers = {"X-Riot-Token": self.api_key}
        
        try:
            self._check_rate_limit()
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.request_times.append(time.time())
            match_ids = response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch match history: {e}")
        
        return match_ids

