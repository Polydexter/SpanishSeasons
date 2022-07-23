import sqlite3


seasons = [i for i in range(2013, 2023)]

# Create connection and  cursor for games.db
con = sqlite3.connect('seasons.db')
cur = con.cursor()


def main():

    # Create new table
    cur.execute("DROP TABLE IF EXISTS standings")
    cur.execute("""CREATE TABLE standings
    (season INTEGER NOT NULL,
    matchday INTEGER NOT NULL,
    position INTEGER,
    team TEXT NOT NULL,
    scored INTEGER,
    conceded INTEGER,
    points INTEGER)""")
    for season in seasons:
        for matchday in range(1,39):
            # Get all the results for a match day
            results = cur.execute("""SELECT *
                FROM games
                WHERE season = ?
                AND matchday = ?""",
                                  (season, matchday))

            # Create table with teams, stats and points as a list of dictionaries
            new_standings = assign_points(results, season, matchday)
            # Sort this table by points, goal difference and goals scored
            sorted_standings = standings_sort(new_standings, matchday)

            # When second half of the season starts
            if matchday > 19:
                # Find groups of teams with equal points to check for head-to-head games
                ties = get_ties(sorted_standings)
                # Each group of ties is a group of teams with equal amount of points
                for group in ties:
                    # Get team names
                    tie_teams = [sorted_standings[i]['team'] for i in group]
                    # Get head-to-head games for each pair of teams in the group
                    hh_games = get_head_to_head(tie_teams, matchday)
                    # If both head-to-head games are played for each pair
                    if None not in hh_games:
                        # Create table with head-to-head stats and points
                        tie_standings = hh_standings(hh_games, tie_teams)
                        # Sort by hh points and goal difference
                        sorted_ties = hh_sort(tie_standings)
                        # Put complete data in each line of tie_standings
                        for i in range(len(sorted_ties)):
                            for line in sorted_standings:
                                if sorted_ties[i]['team'] == line['team']:
                                    sorted_ties[i] = line

                        # Put sorted ties back into general table
                        tie_index = 0
                        for index in group:
                            sorted_standings[index] = sorted_ties[tie_index]
                            tie_index += 1
                    else:
                        continue

            # Assign positions in standings
            for i in range(len(sorted_standings)):
                sorted_standings[i]['position'] = i + 1

            for team in sorted_standings:
                cur.execute("""INSERT INTO standings
                (season, matchday, position, team, scored, conceded, points)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (season, matchday, team['position'], team['team'], team['scored'], team['conceded'], team['points']))

            con.commit()
    con.close()

def get_ties(standings):

    """Takes standings and returns list of groups with equal points"""

    ties = []
    group = []
    for i in range(len(standings) - 1):
        if standings[i]['points'] == standings[i + 1]['points']:
            group += [i + 1]
        else:
            ties += [group]
            group = [i + 1]
    ties += [group]

    return [group for group in ties if len(group) > 1]


def assign_points(results, season, matchday):
    """Takes matchday number, extracts game results, returns unsorted standings with points assigned"""

    # Create a list of dicts to store the standings
    standings = []

    # Assign points game by game
    for row in results:
        # Clarify values from each game
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

    # Add new results to the previous points
    if matchday != 1:
        # Get previous standings as a list
        previous = cur.execute("""SELECT * FROM standings
        WHERE season = ? AND matchday = ?""", (season, matchday - 1))
        # Since new and old standings differ by order of teams, we need to link up teams by iterations
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


def get_head_to_head(teams, matchday):
    """Takes list of positions of teams with equal points
    and returns list of head-to-head games between those teams"""
    # Get team names from list

    hh_games = []
    # Get head-to-head games
    for host in teams:
        for guest in teams:
            if host != guest:
                hh_game = cur.execute("""SELECT * FROM games
                WHERE matchday <= ?
                AND Home = ?
                AND Away = ?""", (matchday, host, guest))
                hh_games += [hh_game.fetchone()]

    return hh_games


def hh_standings(games, teams):

    hh_standings = []
    for team in teams:
        hh_standings += [{
            'team': team,
            'scored': 0,
            'conceded': 0,
            'points': 0,
        }]

    for game in games:
        Home, Away, HG, AG = game[2], game[3], game[4], game[5]
        # For each game two dicts must be created
        home_results = {
            'team': Home,
            'scored': HG,
            'conceded': AG,
            'points': 0
        }
        away_results = {
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
        for team in hh_standings:
            if team['team'] == home_results['team']:
                team['scored'] += home_results['scored']
                team['conceded'] += home_results['conceded']
                team['points'] += home_results['points']
            if team['team'] == away_results['team']:
                team['scored'] += away_results['scored']
                team['conceded'] += away_results['conceded']
                team['points'] += away_results['points']

    return hh_standings


def hh_sort(hh_standings):
    """Takes head-to-head results, returns sorted standings"""
    swaps = 0
    for i in range(len(hh_standings) - 1):
        if hh_standings[i]['points'] < hh_standings[i + 1]['points']:
            hh_standings[i], hh_standings[i +1] = hh_standings[i + 1], hh_standings[i]
            swaps += 1
        elif hh_standings[i]['points'] == hh_standings[i + 1]['points'] \
            and hh_standings[i + 1]['scored'] - hh_standings[i + 1]['conceded'] \
                > hh_standings[i]['scored'] - hh_standings[i]['conceded']:
            hh_standings[i], hh_standings[i +1] = hh_standings[i +1], hh_standings[i]
            swaps += 1
    # Recently added. Delete comment before submission
    if swaps != 0:
        hh_sort(hh_standings)

    return hh_standings


def standings_sort(standings, matchday):
    swaps = 0
    for i in range(len(standings) - 1):
        if standings[i]['points'] < standings[i + 1]['points']:
            swaps += 1
            standings[i], standings[i + 1] = standings[i + 1], standings[i]
        elif standings[i]['points'] == standings[i + 1]['points']:
            standings[i], standings[i + 1], swaps = tie_breaker(standings[i], standings[i + 1], swaps)

    if swaps != 0:
        standings_sort(standings, matchday)

    # assert len(standings) == 20, f"Expected 20 teams, got {len(standings)}"
    return standings


main()
