import sqlite3
from flask import Flask, render_template, redirect, request, url_for, session
from flask_session.__init__ import Session

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/', methods=["GET", "POST"])
def index():

    con = sqlite3.connect('seasons.db')
    cur = con.cursor()
    results = []

    if request.method == "GET":
        data = cur.execute("SELECT * FROM standings WHERE matchday = 38 AND team = 'Barcelona' ORDER BY season DESC")
        for row in data:
            results += [row]
        con.close()
        return render_template("index.html", results=results)
    else:
        session['season'] = request.form.get("season")
        return redirect(url_for('simulation'))



@app.route('/simulation', methods=["GET", "POST"])
def simulation():
    season = session['season']
    if request.method == "GET":

        con = sqlite3.connect('seasons.db')
        cur = con.cursor()
        standings = []
        data = cur.execute("SELECT * FROM standings WHERE matchday = 1 AND season = ?", (season,))
        for row in data:
            standings += [row]

        games = []
        data1 = cur.execute("SELECT * FROM games WHERE season = ? AND matchday = 1", (season,))
        for row in data1:
            games += [row]

        con.close()
    else:

        matchday = request.form.get("matchday")

        con = sqlite3.connect('seasons.db')
        cur = con.cursor()
        standings = []
        data = cur.execute("SELECT * FROM standings WHERE matchday = ? AND season = ?", (matchday, season,))
        for row in data:
            standings += [row]

        games = []
        data = cur.execute("SELECT * FROM games WHERE season = ? AND matchday = ?", (season, matchday))
        for row in data:
            games += [row]
        con.close()
    return render_template("simulation.html", standings=standings, games=games)


app.run()
