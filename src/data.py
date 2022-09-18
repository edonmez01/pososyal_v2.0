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

# Database connection
connection = sqlite3.connect('superlig_database.db')
cursor = connection.cursor()

# Converting the players database to a Python dictionary.
players_dict = {}
for row in cursor.execute('SELECT * FROM players WHERE price > .1'):
    players_dict[row[0]] = row[1:]
