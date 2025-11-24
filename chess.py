import requests
import time
from datetime import datetime, timedelta, timezone
import re
from chess_functions import *
from collections import defaultdict
from dotenv import load_dotenv
import os
import psycopg2 
from psycopg2.extras import execute_values

load_dotenv()

dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")

conn = psycopg2.connect(
    dbname = dbname,
    user = user,
    password = password,
    host = host,
    port = port
)

cur = conn.cursor()

games_count_total = 0

duration_by_date = defaultdict(float)

headers = {
    "User-Agent": "ConnorChessTracker (Personal project; beginner dev; contact: ronnnoc715@yahoo.com)"
}

username = "neerajfrommacungie"

response = requests.get(f"https://api.chess.com/pub/player/{username}", headers=headers)
time.sleep(1)

if response.status_code == 200:
    player_data = response.json()
    player_id = player_data['player_id']
    display_name = player_data.get('name')
    date_joined = datetime.fromtimestamp(player_data.get('joined'), tz=timezone.utc)

else:
        print("Failed to fetch data:", response.status_code)

response = requests.get(f"https://api.chess.com/pub/player/{username}/stats", headers=headers)
time.sleep(1)

if response.status_code == 200:
    player_data = response.json()
    current_rating = player_data['chess_blitz']['last']['rating']

else:
        print("Failed to fetch data:", response.status_code)

insert_player_data(cur, player_id, username, display_name, current_rating, date_joined)

start_input = "2018-05-01"
end_input = "2025-11-23"

start_date = datetime.strptime(start_input, "%Y-%m-%d").date()
end_date =  datetime.strptime(end_input, "%Y-%m-%d").date()

urls = [f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
        for year, month in extract_years_months(start_date, end_date)]

for url in urls:

    games_count_month = 0
    
    response = requests.get(url, headers=headers)
    time.sleep(.2)

    if response.status_code == 200:
        data = response.json()
        for game in data['games']:

            end_time = datetime.fromtimestamp(game['end_time'], tz=timezone.utc)
            date_only = end_time.date()
            pgn = game.get('pgn')

            if not pgn:
                 print(f"[SKIPPED] Game {game.get('url', '(no id)')} has no PGN. {url}")

            if pgn:     
                start_time_match = re.search(r'\[StartTime "(\d{2}:\d{2}:\d{2})"\]', pgn)
                end_time_match = re.search(r'\[EndTime "(\d{2}:\d{2}:\d{2})"\]', pgn)

            if start_time_match and end_time_match:

                start = start_time_match.group(1)
                end = end_time_match.group(1)

                h1, m1, s1 = map(int, start.split(":"))
                h2, m2, s2 = map(int, end.split(":"))

                start_duration = timedelta(hours=h1, minutes=m1, seconds=s1)
                end_duration = timedelta(hours=h2, minutes=m2, seconds=s2)

                if end_duration < start_duration:
                    end_duration += timedelta(days=1)

                duration = end_duration - start_duration
                duration_seconds = duration.total_seconds()

                duration_by_date[date_only] += duration_seconds

            if game['white']['username'] == username:
                rating = game['white']['rating']
                played_as_color = 'white'   

            elif game['black']['username'] == username:
                rating = game['black']['rating']
                played_as_color = 'black'  

            game_id = int(game['url'].rstrip("/").split("/")[-1])
            player_username = username
            
            if played_as_color == 'white':
                opponent_username = game['black']['username']
                opponent_rating = game['black']['rating']

            elif played_as_color == 'black':
                opponent_username = game['white']['username']
                opponent_rating = game['white']['rating']

            result = game[played_as_color]['result']
            rating_after_game = game[played_as_color]['rating']
            time_class = game['time_class']

            start_time = end_time - duration

            games_count_month += 1
            games_count_total += 1

            insert_game_data(cur, game_id, player_username, opponent_username, opponent_rating, played_as_color, result, rating_after_game, time_class, start_time, end_time, duration_seconds, pgn)        
    else:
        print("Failed to fetch data:", response.status_code)

    print(f"{games_count_month} Games fetched from {url}")

print(f"Success! {games_count_total} games stored")

conn.commit()
cur.close()
conn.close()
