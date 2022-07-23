import re
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


def main():
    # Webdriver setup
    options = Options()
    options.headless = True
    # Create an instance of webdriver
    driver = webdriver.Firefox(executable_path=r"C:\Program Files (x86)\Mozilla Maintenance Service\geckodriver.exe", options=options)
    # Setup for future iterations through multiple seasons


    # Data base setup
    # Store the data
    con = sqlite3.connect('seasons.db')
    cur = con.cursor()

    # cur.execute("DROP TABLE IF EXISTS games")
    # cur.execute("CREATE TABLE games (season INTEGER, matchday INTEGER, Home TEXT, Away TEXT, HG INTEGER, AG INTEGER)")

    season = 2022

    url = f"https://www.rsssf.org/tabless/span{season}.html#laliga"
    driver.get(url)
    # Get content from the page by tag name
    content = driver.find_element(By.TAG_NAME, "pre")
    games = get_games(content)

    assert len(games) == 380, f"Expected 380 games per season, got {len(games)}"

    for game in games:
        cur.execute("INSERT INTO games (season, matchday, Home, Away, HG, AG) VALUES (?, ?, ?, ?, ?, ?)",
                    (season, game['matchday'], game['Home'], game['Away'], game['HG'], game['AG']))

    con.commit()
    con.close()

    driver.quit()

def get_games(string):
    """Returns list of dictionaries. Each dict contains info for one game"""
    # define a list
    games = []
    # store the round info
    matchday = 0
    start = string.text.find("Round 1")
    end = string.text.find("Final Table:", start)
    lines = string.text[start:end].strip().splitlines()
    # We got of lines of 4 types: round, date, game, blank
    for line in lines:
        if "Round" in line:
            matchday = int(line.split()[1])
        elif len(line) == 0:
            continue
        elif "[" in line:
            continue
        else:
            pattern = re.compile(r"(\D+)(\S+)-(\S+)\s+(\D+)")
            data = pattern.match(line)
            if data:
                games += [{
                    'matchday': matchday,
                    'Home': data.group(1).strip(),
                    'Away': data.group(4).strip(),
                    'HG': int(data.group(2)),
                    'AG': int(data.group(3)),
                }]
    return games


if __name__ == '__main__':
    main()


