def insert_player_data(cur, player_id, username, display_name=None, current_rating=None, date_joined=None):
    cur.execute("""
        INSERT INTO players (player_id, username, display_name, current_rating, date_joined, last_updated)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (player_id) DO UPDATE
        SET username = EXCLUDED.username,
            current_rating = EXCLUDED.current_rating,
            last_updated = NOW();
    """, (player_id, username, display_name, current_rating, date_joined))

def insert_game_data(cur, game_id, player_username, opponent_username, opponent_rating, played_as_color, result, rating_after_game, time_class, start_time, end_time, duration_seconds, pgn):
    cur.execute("""
        INSERT INTO games (game_id, player_username, opponent_username, opponent_rating, played_as_color, result, rating_after_game, time_class, start_time, end_time, duration_seconds, pgn)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (game_id) DO NOTHING;
    """, (game_id, player_username, opponent_username, opponent_rating, played_as_color, result, rating_after_game, time_class, start_time, end_time, duration_seconds, pgn))

def extract_years_months(start, end):
    year = start.year
    month = start.month

    while (year, month) <= (end.year, end.month):

        yield year, month
    
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
