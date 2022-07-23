# BarçaSeasons - CS50x Final Project

This simple web application was created as a final project for the CS50x course “Introduction to Computer Science”.
The idea came from personal experience as a football supporter (namely, of the Football Club “Barcelona”).

### Purpose of the app

After many years of rooting for the club, I often struggle to recall the tournament significance of a particular game (for example, when watching highlights).
Existing free services provide results for particular games or the final standings for a season. Services that dynamically show past title races and intermediary standings
are hard to find.

The goal of the app is to fill this gap and to provide a simple tool to check Spanish LaLiga table at any given moment during past ten seasons.

### How to use

The user interface is pretty simple. There are two webpages: "Home" and "Simulation". The home page shows the list of seasons available.
Users can pick a season for simulation by clicking a button with dates (i.e. "2021/2022'). After picking a season, the user is redirected to the "Simulation" page.
"Simulation" page displays the standings after each consecutive round and corresponding games with scores. 
Navigation buttons ("First", "Previous", "Next", "Last") allow users to move to the next or to the previous round as well as to jump
straight to the end or to the beginning of the season.

### Implementation

Standings are calculated by a script ("standings.py") which takes as an input games and scores. The script assigns points and keeps track of secondary data (i.e. goal difference).
Then it sorts the teams in accordance with official LaLiga regulations. The main sorting criterion is the amount of points. When multiple teams have equal points, the script uses tie-breaker criteria:
- results of head-to-head games (only when both head-to-head games have already been played)
- head-to-head goal difference
- total goal difference
- total goals scored

Data with games and scores was taken from the site of [RSSSF project](http://www.rsssf.com/) and stored in SQLite database.
Since necessary information at RSSSF page is stored as a single HTML block with pre-formatted text, I implemented another script ("parser.py")
to extract and store the information by using tools from Selenium and Re libraries.

The Flask-application contains routes with embedded SQL SELECT-queries. Since all the data is preprocessed and stored in the database, the app itself is responsible
only for displaying results of the queries. This structure of the app assures quick performance.

### Technologies used

- languages: Python, SQL, HTML, CSS
- frameworks: Flask, Bootstrap
- Python libraries: sqlite3, selenium, re

### Possible improvements
- More precision

Tie breaker rules are implemented as per current official regulations. These regulations differ from those in effect several years ago due to gradual minor modifications.
These differences cause slight imprecisions in the app for distant seasons. This issue could be resolved by additional investigation of the history of LaLiga regulations
and by some changes in the logic of the sorting script.

- Better visualization

Later on, the application may be augmented by a system of dynamic visualization, for example with D3.js tools.
