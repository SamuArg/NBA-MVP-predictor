from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

class Scrap:
    """
    Scrapes NBA statistics from basketball-reference.com.
    
    Handles scraping of:
    - MVP voting results
    - Team standings
    - Advanced statistics
    - Per game statistics
    
    Attributes:
        first_year (int): Start season year
        last_year (int): End season year
    """

    def __init__(self, first_year, last_year):
        """
        Args:
            first_year: Starting season year
            last_year: Ending season year
        """
        self.first_year = first_year
        self.last_year = last_year
    
    def scrap_mvps(self, save=False) -> pd.DataFrame:
        """
        Scrape historical MVP voting results.

        Args:
            save (bool): Save results to CSV if True

        Returns:
            pd.DataFrame: MVP voting data
        """
        all_rows = []
        for year in range(self.first_year, self.last_year + 1):
            url = f"https://www.basketball-reference.com/awards/awards_{year}.html"
            html = urlopen(url)
            soup = BeautifulSoup(html, "lxml")
            table = soup.find("table")
            headers = [th.getText() for th in table.findAll("tr", limit=2)[1].findAll("th")]
            headers[0] = "Year"
            rows = table.findAll('tr')[2:]
            rows_data = [[td.getText() for td in rows[i].findAll('td')]
                            for i in range(len(rows))]
            for i in range(len(rows_data)):
                rows_data[i].insert(0, year)
            all_rows.extend(rows_data)
            print("MVPs for Season", year, "done")
            time.sleep(5)
        mvps = pd.DataFrame(all_rows, columns = headers)
        if save:
            mvps.to_csv(f"../data/raw/{self.first_year}_{self.last_year}_mvps.csv", index=False)
        return mvps
        
    
    def scrap_standings(self, save=False) -> pd.DataFrame:
        all_rows = pd.DataFrame()
        for year in range(self.first_year, self.last_year + 1):
            url = f"https://www.basketball-reference.com/leagues/NBA_{year}_standings.html#expanded_standings"
            html = urlopen(url)
            soup = BeautifulSoup(html, "lxml")
            tables = soup.findAll("table")
            east_table = tables[0]
            west_table = tables[1]
            east_data, headers = self.scrap_conference(east_table, year)
            west_data, _ = self.scrap_conference(west_table, year)
            east = pd.DataFrame(east_data, columns = headers)
            west = pd.DataFrame(west_data, columns = headers)
            league = pd.concat([east, west])
            league = league.sort_values(by=["W/L%"], ascending=False)
            league["seed"] = range(1, len(league) + 1)
            all_rows = pd.concat([all_rows, league])
            print("Standing for season", year, "done")
            time.sleep(5)
        if save:
            all_rows.to_csv(f"../data/raw/{self.first_year}_{self.last_year}_standings.csv", index=False)
        return all_rows
        
    
    def scrap_conference(self, table, year) -> pd.DataFrame:
        headers = [th.getText() for th in table.findAll("tr", limit=2)[0].findAll("th")]
        headers[0] = "Year"
        headers.insert(1, "Team")
        rows = table.findAll('tr')[1:]
        rows_data = [[td.getText() for td in rows[i].findAll('td')]
                    for i in range(len(rows))]
        teams = [[td.getText() for td in rows[i].findAll('th')]
                for i in range(len(rows))]
        for i in range(len(rows_data)):
                rows_data[i].insert(0, year)
                clean_team = teams[i][0].replace("*", "")
                clean_team = re.sub(r'\(\d*\)', "", clean_team).strip()
                rows_data[i].insert(1, clean_team)
        return rows_data, headers
    
    def scrap_advanced(self, save=False) -> pd.DataFrame:
        all_rows = []
        for year in range(self.first_year, self.last_year + 1):
            url = f"https://www.basketball-reference.com/leagues/NBA_{year}_advanced.html"
            html = urlopen(url)
            soup = BeautifulSoup(html, "lxml")
            table = soup.find("table")
            headers = [th.getText() for th in table.findAll("tr", limit=2)[0].findAll("th")]
            headers[0] = "Year"
            rows = table.findAll('tr')[1:]
            rows_data = [[td.getText() for td in rows[i].findAll('td')]
                            for i in range(len(rows))]
            for i in range(len(rows_data)):
                rows_data[i].insert(0, year)
            all_rows.extend(rows_data)
            print("Advanced for season", year, "done")
            time.sleep(5)
        advanced = pd.DataFrame(all_rows, columns = headers)
        if save:
            advanced.to_csv(f"../data/raw/{self.first_year}_{self.last_year}_advanced.csv", index=False)
        return advanced
        
    def scrap_per_game(self, save=False) -> pd.DataFrame:
        all_rows = []
        for year in range(self.first_year, self.last_year + 1):
            url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
            html = urlopen(url)
            soup = BeautifulSoup(html, "lxml")
            table = soup.find("table")
            headers = [th.getText() for th in table.findAll("tr", limit=2)[0].findAll("th")]
            headers[0] = "Year"
            rows = table.findAll('tr')[1:]
            rows_data = [[td.getText() for td in rows[i].findAll('td')]
                            for i in range(len(rows))]
            for i in range(len(rows_data)):
                rows_data[i].insert(0, year)
            all_rows.extend(rows_data)
            print("Per game for season", year, "done")
            time.sleep(5)
        per_game = pd.DataFrame(all_rows, columns = headers)
        if save:
            per_game.to_csv(f"../data/raw/{self.first_year}_{self.last_year}_per_game.csv", index=False)
        return per_game