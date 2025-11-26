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
correct_username = None

headers = {
    "User-Agent": "ConnorChessTracker (Personal project; beginner dev; contact: ronnnoc715@yahoo.com)"
}

username = "neerajfrommacungie".lower()

response = requests.get(f"https://api.chess.com/pub/player/{username}", headers=headers)
time.sleep(1)

if response.status_code == 200:
    player_data = response.json()
    player_id = player_data['player_id']
    display_name = player_data.get('name')
    date_joined = datetime.fromtimestamp(player_data.get('joined'), tz=timezone.utc)
    profile_image = player_data['avatar']

else:
        print("Failed to fetch data:", response.status_code)

response = requests.get(f"https://api.chess.com/pub/player/{username}/stats", headers=headers)
time.sleep(1)

if response.status_code == 200:
    player_data = response.json()
    current_rating = player_data['chess_blitz']['last']['rating']

else:
        print("Failed to fetch data:", response.status_code)

insert_player_data(cur, player_id, username, display_name, current_rating, date_joined, profile_image)

# start_input = "2025-11-01"
# end_input = "2025-11-23"

# start_date = datetime.strptime(start_input, "%Y-%m-%d").date()
# end_date =  datetime.strptime(end_input, "%Y-%m-%d").date()

start_date = date_joined.date()
end_date = datetime.now(timezone.utc).date()

urls = [f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
        for year, month in extract_years_months(start_date, end_date)]

print("Starting game ingestion...")

start_timer = datetime.now()

for url in urls:

    games_count_month = 0
    
    response = requests.get(url, headers=headers)
    time.sleep(.2)

    if response.status_code == 200:
        data = response.json()
        for game in data['games']:

            if game['time_class'] not in ('rapid', 'bullet', 'blitz'):
                 continue

            end_time = datetime.fromtimestamp(game['end_time'], tz=timezone.utc)
            date_only = end_time.date()

            pgn = game.get('pgn')

            if not pgn:
                 print(f"[SKIPPED] Game {game.get('url', '(no id)')} has no PGN. {url}")
                 continue

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

            if correct_username == None:
                white_username = game['white']['username']
                black_username = game['black']['username']

                if white_username.lower() == username:
                     correct_username = white_username
                elif black_username.lower() == username:
                     correct_username = black_username

            if game['white']['username'].lower() == username:
                rating = game['white']['rating']
                played_as_color = 'white'   

            elif game['black']['username'].lower() == username:
                rating = game['black']['rating']
                played_as_color = 'black'  

            game_id = int(game['url'].rstrip("/").split("/")[-1])
            player_username = username

            if played_as_color == 'white':
                opponent_username = game['black']['username'].lower()
                opponent_rating = game['black']['rating']

            elif played_as_color == 'black':
                opponent_username = game['white']['username'].lower()
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

update_player_username(cur, correct_username, player_id)

last_game_time = get_last_game_time(cur, correct_username)

if last_game_time is not None:
    update_last_game_time(cur, last_game_time, player_id)

end_timer = datetime.now()

print(f"Success! {games_count_total} games stored. Time elapsed: {end_timer - start_timer}")

conn.commit()
cur.close()
conn.close()
