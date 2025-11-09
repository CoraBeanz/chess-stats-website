import matplotlib.pyplot as plt

def extract_years_months(start, end):
    """
    Yield (year, month) pairs from start to end date inclusive.
    Used to build URLs for monthly Chess.com archives.
    """
    
    year = start.year
    month = start.month

    while (year, month) <= (end.year, end.month):

        yield year, month
    
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

def plot_date_ratings(dates, ratings):
    plt.figure(figsize=(10, 6))
    plt.plot(dates, ratings, marker='o')
    plt.title(f"Neer's Blitz Rating History in 2025")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.grid(True)
    plt.tight_layout()

def plot_date_durations(dates, durations):
    plt.figure(figsize=(10, 6))
    plt.plot(dates, durations, marker='o')
    plt.title(f"Neer's Blitz Time Spent per Day")
    plt.xlabel("Date")
    plt.ylabel("Duration (min)")
    plt.grid(True)
    plt.tight_layout()

def plot_rating_and_duration_dual_axis(dates_for_rating, ratings, dates_for_duration, durations_in_minutes):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot ratings on the left Y-axis
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Rating", color="blue")
    ax1.plot(dates_for_rating, ratings, marker='o', linestyle='-', color="blue", label="Rating")
    ax1.tick_params(axis='y', labelcolor="blue")

    # Create a second Y-axis for duration (right side)
    ax2 = ax1.twinx()
    ax2.set_ylabel("Duration (minutes)", color="red")
    ax2.plot(dates_for_duration, durations_in_minutes, marker='o', linestyle='-', color="red", label="Duration")
    ax2.tick_params(axis='y', labelcolor="red")

    # Title and grid
    plt.title("Neer's Blitz Rating vs. Daily Time Spent")
    fig.tight_layout()
    plt.grid(True)
    plt.show()

def plot_rating_colored_by_playtime(dates, ratings, duration_by_date):
    """
    Creates a scatter plot of (date, rating) points where each dot's color
    reflects how much time was spent playing on that date.
    
    - dates: list of datetime objects (per game)
    - ratings: list of ratings corresponding to each game
    - duration_by_date: dict mapping date -> total seconds played
    """

    # Extract just the date (no time) for matching with daily durations
    game_days = [dt.date() for dt in dates]

    # Get playtime (in minutes) for each game based on that day
    playtimes = [duration_by_date.get(day, 0) / 60 for day in game_days]

    # Create the heat-colored scatter plot
    plt.figure(figsize=(12, 6))
    scatter = plt.scatter(game_days, ratings, c=playtimes, cmap='hot_r', edgecolor='k', s=40)
    
    # Add colorbar legend
    cbar = plt.colorbar(scatter)
    cbar.set_label("Time Played That Day (minutes)")

    # Labels and layout
    plt.title("Rating Over Time Colored by Daily Time Spent")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.grid(True)
    plt.tight_layout()
    plt.show()