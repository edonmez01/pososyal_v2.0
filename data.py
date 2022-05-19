from dotenv import load_dotenv
import os
import sqlite3

# Pulling the environment variables from the .env file.
load_dotenv()
NEXT_WEEK = os.getenv('NEXT_WEEK')
TOTAL_BUDGET = float(os.getenv('TOTAL_BUDGET'))
MISSING_PLAYERS = os.getenv('MISSING_PLAYERS')
if MISSING_PLAYERS:
    MISSING_PLAYERS = set(int(s) for s in MISSING_PLAYERS.split(','))
else:
    MISSING_PLAYERS = set()
GUARANTEED = os.getenv('GUARANTEED')
if GUARANTEED:
    GUARANTEED = set(int(s) for s in GUARANTEED.split(','))
else:
    GUARANTEED = set()

BYE_TEAMS = set()

# Database connection
connection = sqlite3.connect('superlig_database.db')
cursor = connection.cursor()

# Converting the players database to a Python dictionary.
players_dict = {}
for row in cursor.execute('SELECT * FROM players WHERE price > .1'):
    players_dict[row[0]] = row[1:]

# Converting the matches database to a Python dictionary.
matches_dict_raw = {}
for row in cursor.execute('SELECT * FROM matches WHERE winner IS NULL'):
    matches_dict_raw[row[0]] = row[1:]

matches_dict = {}
for match_id, match_data in matches_dict_raw.items():
    home = match_data[0]
    away = match_data[1]
    try:
        home_prediction = int(match_data[5])
        away_prediction = int(match_data[6])
    except TypeError:  # If the predictions do not exist yet
        print(f'Skipping {home} - {away}')
        home_prediction = None
        away_prediction = None
    matches_dict[match_id] = {'home': home, 'away': away, 'home_prediction': home_prediction,
                              'away_prediction': away_prediction}

# Dictionary of all teams in the league, and predictions of their next matches.
teams = {  # team: (score_prediction, concede_prediction)
    'alanya': (-1, -1),
    'ankara': (-1, -1),
    'antalya': (-1, -1),
    'basaksehir': (-1, -1),
    'besiktas': (-1, -1),
    'denizli': (-1, -1),
    'erzurum': (-1, -1),
    'fenerbahce': (-1, -1),
    'galatasaray': (-1, -1),
    'gaziantep': (-1, -1),
    'gencler': (-1, -1),
    'goztepe': (-1, -1),
    'hatay': (-1, -1),
    'karagumruk': (-1, -1),
    'kasimpasa': (-1, -1),
    'kayseri': (-1, -1),
    'konya': (-1, -1),
    'malatya': (-1, -1),
    'rize': (-1, -1),
    'sivas': (-1, -1),
    'trabzon': (-1, -1)
}

for match_id, match_data in matches_dict.items():
    if str(match_id)[:-2] == NEXT_WEEK:
        home_prediction = match_data['home_prediction']
        away_prediction = match_data['away_prediction']
        teams[match_data['home']] = (home_prediction, away_prediction)
        teams[match_data['away']] = (away_prediction, home_prediction)

# If a team doesn't have a score prediction, we can understand that it won't play in the next week.
for team, pred in teams.items():
    if pred == (-1, -1):
        BYE_TEAMS.add(team)
