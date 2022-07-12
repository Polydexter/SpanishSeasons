import sqlite3

season = 2022

# Create connection and  cursor for games.db
con = sqlite3.connect('seasons.db')
cur = con.cursor()


def main():

    # Create new table
    cur.execute("""CREATE TABLE standings
    (season INTEGER NOT NULL,
    matchday INTEGER NOT NULL,
    position INTEGER,
    team TEXT NOT NULL,
    scored INTEGER,
    conceded INTEGER,
    points INTEGER)""")

    for matchday in range(1, 39):
        # Create a list of dictionaries. One dict per team to sort later
        new_standings = assign_points(season, matchday)
        sorted_standings = standings_sort(new_standings)
        # Assign positions in standings
        for i in range (len(sorted_standings)):
            sorted_standings[i]['position'] = i + 1

        for team in sorted_standings:
            print(team)
            cur.execute("""INSERT INTO standings
            (season, matchday, position, team, scored, conceded, points)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (season, matchday, team['position'], team['team'], team['scored'], team['conceded'], team['points']))

        con.commit()
    con.close()


def assign_points(season, matchday):
    # Get all the results from a match day
    results = cur.execute("""SELECT *
    FROM games
    WHERE season = ?
    AND matchday = ?""",
                          (season, matchday))

    # Create a list of dicts to store the standings
    standings = []

    # Assign points game by game
    for row in results:
        # Get explicitly named values from each game
        Home, Away, HG, AG = row[2], row[3], row[4], row[5]
        # For each game two dicts must be created
        home_results = {
            'season': season,
            'matchday': matchday,
            'team': Home,
            'scored': HG,
            'conceded': AG,
            'points': 0
        }
        away_results = {
            'season': season,
            'matchday': matchday,
            'team': Away,
            'scored': AG,
            'conceded': HG,
            'points': 0
        }
        # Three possible results:
        if HG == AG:
            home_results['points'] = 1
            away_results['points'] = 1
        elif HG > AG:
            home_results['points'] = 3
        else:
            away_results['points'] = 3

        # finish each iteration by updating
        standings += [home_results]
        standings += [away_results]

    if matchday != 1:
        # Get previous standings as a list
        previous = cur.execute("""SELECT * FROM standings
        WHERE season = ? AND matchday = ?""", (season, matchday - 1))

# TODO: link up current and previous standings data
        for row in previous:
            for team in standings:
            # Update team with corresponding data from previous standings
                if team['team'] == row[3]:
                    team['scored'] += row[4]
                    team['conceded'] += row[5]
                    team['points'] += row[6]

    return standings


def tie_breaker(team1, team2, swaps):

    if team1['scored'] - team1['conceded'] < team2['scored'] - team2['conceded']:
        swaps += 1
        team1, team2 = team2, team1
    elif (team1['scored'] - team1['conceded']) == (team2['scored'] - team2['conceded']) \
            and team1['scored'] < team2['scored']:
        swaps += 1
        team1, team2 = team2, team1

    return team1, team2, swaps

# TODO: head-to-head function


def standings_sort(standings):
    swaps = 0
    for i in range(len(standings) - 1):
        if standings[i]['points'] < standings[i + 1]['points']:
            swaps += 1
            standings[i], standings[i + 1] = standings[i + 1], standings[i]
        elif standings[i]['points'] == standings[i + 1]['points']:
            standings[i], standings[i + 1], swaps = tie_breaker(standings[i], standings[i + 1], swaps)

    if swaps != 0:
        standings_sort(standings)

    assert len(standings) == 20, f"Expected 20 teams, got {len(standings)}"
    return standings


main()
