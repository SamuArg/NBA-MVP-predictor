import pandas as pd
from sklearn.preprocessing import StandardScaler

class Processed:
    def __init__(self, mvps: pd.DataFrame, standings: pd.DataFrame, advanced: pd.DataFrame, per_game: pd.DataFrame):
        self.mvps = mvps
        self.standings = standings
        self.advanced = advanced
        self.per_game = per_game
        self.processed = None
        
    def remove_divisions(self) -> pd.DataFrame:
        self.standings = self.standings[self.standings.Team.str.contains('Division') == False]
        return self.standings
    
    def clean_stats_standings(self) -> pd.DataFrame:
        self.standings = self.standings.drop(columns=["W","L",'GB', 'PS/G', 'PA/G', 'SRS'])
        return self.standings
    
    def update_team_names(self) -> pd.DataFrame:
        team_map = {
            'Atlanta Hawks': 'ATL',
            'Boston Celtics': 'BOS',
            'Brooklyn Nets': 'BRK',
            'Charlotte Hornets': 'CHH',
            'Chicago Bulls': 'CHI',
            'Cleveland Cavaliers': 'CLE',
            'Dallas Mavericks': 'DAL',
            'Denver Nuggets': 'DEN',
            'Detroit Pistons': 'DET',
            'Golden State Warriors': 'GSW',
            'Houston Rockets': 'HOU',
            'Indiana Pacers': 'IND',
            'Los Angeles Clippers': 'LAC',
            'Los Angeles Lakers': 'LAL',
            'Memphis Grizzlies': 'MEM',
            'Miami Heat': 'MIA',
            'Milwaukee Bucks': 'MIL',
            'Minnesota Timberwolves': 'MIN',
            'New Orleans Pelicans': 'NOP',
            'New York Knicks': 'NYK',
            'Oklahoma City Thunder': 'OKC',
            'Orlando Magic': 'ORL',
            'Philadelphia 76ers': 'PHI',
            'Phoenix Suns': 'PHO',
            'Portland Trail Blazers': 'POR',
            'Sacramento Kings': 'SAC',
            'San Antonio Spurs': 'SAS',
            'Toronto Raptors': 'TOR',
            'Utah Jazz': 'UTA',
            'Washington Wizards': 'WAS',
            'Washington Bullets': 'WSB',
            "New Jersey Nets": "NJN",
            "Kansas City Kings": "KCK",
            "San Diego Clippers": "SDC",
            "Seattle SuperSonics": "SEA",
            "Vancouver Grizzlies": "VAN",
            "New Orleans Hornets": "NOH",
            "Charlotte Bobcats": "CHA",
            "New Orleans/Oklahoma City Hornets": "NOK",
        }
        self.standings['Team'] = self.standings['Team'].map(team_map)
        return self.standings
    
    def clean_mvps(self) -> pd.DataFrame:
        self.mvps = self.mvps.drop(columns=["Age", "First", "Pts Won", "Pts Max", "WS", "WS/48", "G", "MP", "PTS", "TRB", "AST", "STL", "BLK", "FG%", "3P%", "FT%", "Tm"])
        return self.mvps
    
    def merge_stats(self) -> pd.DataFrame:
        self.advanced = pd.merge(self.advanced, self.standings[['Year', 'Team', 'W/L%', "seed"]], left_on=['Year', 'Team'], right_on=["Year", "Team"], how='left')
        self.advanced = self.advanced.drop(columns=["MP"])
        self.per_game = self.per_game.drop(columns=["Team", "Age", "G", "GS", "Pos", "Awards"])
        self.advanced = pd.merge(self.advanced, self.per_game, left_on=['Year', 'Player'], right_on=["Year", "Player"], how='left')
        self.advanced = self.advanced.drop_duplicates(subset=['Player', 'Year'], keep='first')
        self.advanced = self.advanced[self.advanced.Team.str.contains('TOT') == False]
        self.dvanced = self.advanced[self.advanced.Team.str.contains('TM') == False]
        self.advanced = self.advanced.drop(columns=["Pos", "WS", "Awards", "GS"])
        self.processed = self.advanced[self.advanced.Player.str.contains('League') == False]
        return self.processed
    
    def merge_stats_mvps(self) -> pd.DataFrame:
        self.processed = pd.merge(self.processed, self.mvps, on=['Year', 'Player'], how="left")
        self.processed.fillna(0, inplace=True)
        return self.processed
    
    def remove_bad_players(self) -> pd.DataFrame:
        self.processed = self.processed.dropna().astype({"PER": float, "W/L%": float, "MP": float})
        self.processed = self.processed[self.processed["PER"] > 18]
        self.processed = self.processed[self.processed["W/L%"] > 0.5]
        self.processed = self.processed[self.processed["MP"] > 30]
        return self.processed
    
    def scale(self) -> pd.DataFrame:
        scaler = StandardScaler()
        non_numeric_cols = ["Player", "Year", "Team"]
        cols_to_convert = [col for col in self.processed.columns if col not in non_numeric_cols]
        for col in cols_to_convert:
            self.processed[col] = pd.to_numeric(self.processed[col], errors='coerce')
        processed_numeric = self.processed.groupby('Year').apply(lambda x: pd.DataFrame(
            scaler.fit_transform(x.drop(columns=non_numeric_cols)), 
            columns=x.columns.drop(non_numeric_cols)
        )).reset_index(drop=True)
        processed = pd.concat([processed_numeric, self.processed[non_numeric_cols].reset_index(drop=True)], axis=1)
        self.processed = processed
        return self.processed
    
    def process_with_mvps(self) -> pd.DataFrame:
        self.remove_divisions()
        self.clean_stats_standings()
        self.update_team_names()
        self.clean_mvps()
        self.merge_stats()
        self.merge_stats_mvps()
        self.remove_bad_players()
        self.scale()
        return self.processed
    
    def process_without_mvps(self) -> pd.DataFrame:
        self.remove_divisions()
        self.clean_stats_standings()
        self.update_team_names()
        self.merge_stats()
        self.remove_bad_players()
        self.scale()
        return self.processed