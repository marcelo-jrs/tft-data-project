# TFT Match Data Collector

A Python tool for collecting Teamfight Tactics match data from the Riot Games API.

## Current Status: Data Collection

The script currently:
- Fetches Challenger players from KR server
- Gets their match history (50 matches per player)
- Downloads detailed match data
- Saves to CSV files: participants, traits, units and game metadata

Data is stored in `data/checkpoint/[timestamp]/` with batch files and consolidated in `data/final/`.

Future ML Applications

The collected data will be used to train various machine learning models exploring different aspects of TFT gameplay:

- Classification: Predict Top 4 finishes based on final composition
- Clustering: Identify common composition archetypes (fast 9, reroll, vertical, traits)
- Recommendation: Suggest optimal item combinations for champions
- Regression: Determine optimal trait depth and investment strategies
- Pattern Discovery: Uncover winning strategies and feature importance

Each approach offers different insights into game mechanics and player strategies.
