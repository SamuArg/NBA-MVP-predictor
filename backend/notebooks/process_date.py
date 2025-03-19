import pandas as pd
from scripts.Processed import Processed

mvps = pd.read_csv('data/raw/1981_2024_mvps.csv')
standings = pd.read_csv('data/raw/1981_2024_standings.csv')
advanced = pd.read_csv('data/raw/1981_2024_advanced.csv')
per_game = pd.read_csv('data/raw/1981_2024_per_game.csv')
pro = Processed(mvps, standings, advanced, per_game)
print(standings.head(5))

standings = pro.remove_divisions()
print(standings.head(5))

standings = pro.clean_stats_standings()
print(standings.head(5))

standings = pro.update_team_names()
print(standings.head(5))

mvps = pro.clean_mvps()
print(mvps.head(5))

mvps = pro.merge_stats()

mvps = pro.merge_stats_mvps()
print(mvps.head(5))

mvps_scaled = pro.scale()
print(mvps_scaled.head(5))
mvps_scaled.to_csv("data/processed/mvps.csv", index=False)
