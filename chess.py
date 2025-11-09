# Script to fetch Chess.com blitz games for a given user within a date range,
# extract rating and game duration data, and plot rating progression over time.

import requests
import time
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import re
from chess_functions import *
from collections import defaultdict

dates = []
ratings = []
durations = []
duration_by_date = defaultdict(float)

headers = {
    "User-Agent": "ConnorChessTracker (Personal project; beginner dev; contact: ronnnoc715@yahoo.com)"
}

username = "neerajfrommacungie"

start_input = "2025-01-01"
end_input = "2025-10-28"

start_date = datetime.strptime(start_input, "%Y-%m-%d").date()
end_date =  datetime.strptime(end_input, "%Y-%m-%d").date()

urls = [f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
        for year, month in extract_years_months(start_date, end_date)]

for url in urls:

#    print(url)
    
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

#           print(date)

            start_time_match = re.search(r'\[StartTime "(\d{2}:\d{2}:\d{2})"\]', game['pgn'])
            end_time_match = re.search(r'\[EndTime "(\d{2}:\d{2}:\d{2})"\]', game['pgn'])

            start = start_time_match.group(1)
            end = end_time_match.group(1)

            format = "%H:%M:%S"

            start_time = datetime.strptime(start, format)
            end_time = datetime.strptime(end, format)

            if end_time < start_time:
                end_time += timedelta(days=1)

            duration = end_time - start_time
            seconds = duration.total_seconds()

            duration_by_date[date_only] += seconds

            durations.append(seconds)

#            print(f"{end} - {start} = {seconds}") 

            if game['white']['username'] == username:
                rating = game['white']['rating']
                ratings.append(rating)   

            elif game['black']['username'] == username:
                rating = game['black']['rating']
                ratings.append(rating)

    #    print(f"Blitz Rating: {data['chess_blitz']['last']['rating']}")
    else:
        print("Failed to fetch data:", response.status_code)

sorted_days = sorted(duration_by_date)
daily_minutes = [duration_by_date[day] / 60 for day in sorted_days]

plot_date_durations(sorted_days, daily_minutes)
plot_date_ratings(dates, ratings)
plot_rating_and_duration_dual_axis(dates, ratings, sorted_days, daily_minutes)
plot_rating_colored_by_playtime(dates, ratings, duration_by_date)
plt.show()