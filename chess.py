import requests
import time
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
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

dates = []
ratings = []
durations = []
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

else:
        print("Failed to fetch data:", response.status_code)

response = requests.get(f"https://api.chess.com/pub/player/{username}/stats", headers=headers)
time.sleep(1)

if response.status_code == 200:
    player_data = response.json()
    current_rating = player_data['chess_blitz']['last']['rating']

else:
        print("Failed to fetch data:", response.status_code)

insert_player_data(cur, player_id, username, display_name, current_rating)

start_input = "2025-01-01"
end_input = "2025-11-08"

start_date = datetime.strptime(start_input, "%Y-%m-%d").date()
end_date =  datetime.strptime(end_input, "%Y-%m-%d").date()

urls = [f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
        for year, month in extract_years_months(start_date, end_date)]

for url in urls:
    
    response = requests.get(url, headers=headers)
    time.sleep(1)

    if response.status_code == 200:
        data = response.json()
        for game in data['games']:

            if game['time_class'] != 'blitz':
                continue

            full_date = datetime.fromtimestamp(game['end_time'])
            dates.append(full_date)

            date_only = full_date.date()

            start_time_match = re.search(r'\[StartTime "(\d{2}:\d{2}:\d{2})"\]', game['pgn'])
            end_time_match = re.search(r'\[EndTime "(\d{2}:\d{2}:\d{2})"\]', game['pgn'])

            start = start_time_match.group(1)
            end = end_time_match.group(1)

            format = "%H:%M:%S"

            start_time_day = datetime.strptime(start, format).time()
            end_time_day = datetime.strptime(end, format).time()

            start_time = datetime.combine(date_only, start_time_day)
            end_time = datetime.combine(date_only, end_time_day)

            if end_time < start_time:
                end_time += timedelta(days=1)

            duration = end_time - start_time
            duration_seconds = duration.total_seconds()

            duration_by_date[date_only] += duration_seconds

            durations.append(duration_seconds)

            if game['white']['username'] == username:
                rating = game['white']['rating']
                ratings.append(rating)
                played_as_color = 'white'   

            elif game['black']['username'] == username:
                rating = game['black']['rating']
                ratings.append(rating)
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
            pgn = game['pgn']

            insert_game_data(cur, game_id, player_username, opponent_username, opponent_rating, played_as_color, result, rating_after_game, time_class, start_time, end_time, duration_seconds, pgn)
     
    else:
        print("Failed to fetch data:", response.status_code)

conn.commit()
cur.close()
conn.close()

sorted_days = sorted(duration_by_date)
daily_minutes = [duration_by_date[day] / 60 for day in sorted_days]

# plot_date_durations(sorted_days, daily_minutes)
# plot_date_ratings(dates, ratings)
# plot_rating_and_duration_dual_axis(dates, ratings, sorted_days, daily_minutes)
# plot_rating_colored_by_playtime(dates, ratings, duration_by_date)
# plt.show()