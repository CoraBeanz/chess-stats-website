import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import pandas as pd

def plot_blitz_rank_vs_date(df):
    #filtering out unwanted data (keeping only 5 min blitz games)
    blitz_df = df[(df['time_class'] == 'blitz') & (df['duration_seconds'] < 600)]
    blitz_df = blitz_df[blitz_df['pgn'].notna()]
    blitz_df = blitz_df.sort_values(by=['game_id'], ascending = True).reset_index(drop=True)
    blitz_df['index_col'] = blitz_df.index

    blitz_df.plot(kind='scatter', x='index_col', y='rating_after_game')
    plt.scatter(blitz_df.index, blitz_df['rating_after_game'], s=1)
    plt.xlabel('Game Played')
    plt.ylabel('Rating')
    plt.title('Game Played vs Rating')
    plt.show()
    return

def win_loss_result_vs_other_features(df):
    #Clean the dataframe of non-blitz games
    unwanted = ['bughousepartnerlose']
    df = df[~df['result'].isin(unwanted)]

    #Replace all the results with -1 for loss, 0 for draw, 1 for win
    df['result'] = df['result'].replace(['resigned', 'timeout', 'checkmated', 'abandoned'], -1)
    df['result'] = df['result'].replace(['agreed', 'insufficient', 'repetition', 'timevsinsufficient', 'stalemate', '50move'], 0)
    df['result'] = df['result'].replace('win', 1)

    #replace 'played_as_color' with binary, white = 1 black = 0
    df['played_as_color'] = df['played_as_color'].replace({'black': 0, 'white': 1})

    #month
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    #calculations
    df['rating_diff'] = df['opponent_rating'] - df['rating_after_game']
    biggest_win = df['rating_diff'].max()
    biggest_loss = df['rating_diff'].min()
    print(f'Neerajs biggest win was against a player +{biggest_win} his elo.')
    print(f'Neerajs biggest loss was against a player {biggest_loss} his elo')
    print(df[df['rating_diff'] == biggest_loss])

    #plot
    color_map = { -1: 'red', 0: 'green', 1: 'blue' }
    colors = df['result'].map(color_map)

    #Make classifier on win/lose (no ties)
    df_binary = df[df['result'] != 0]
    X = df_binary[['rating_diff', 'rating_after_game', 'opponent_rating', 'duration_seconds', 'played_as_color', 'month', 'year']]
    y = df_binary['result']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression().fit(X_scaled, y)

    for feature, weight in zip(X.columns, model.coef_[0]):
        print(f"{feature}: {weight:.4f}")

    plt.scatter(
        df['rating_diff'],
        df['rating_after_game'],
        c=colors,
        alpha=0.6
    )
    legend_handles = [
    mpatches.Patch(color='red', label='Loss (-1)'),
    mpatches.Patch(color='green', label='Draw (0)'),
    mpatches.Patch(color='blue', label='Win (1)')
    ]
    plt.legend(handles=legend_handles)
    plt.xlabel("Difference in Ratings (+ is higher rank, - is lower rank opponent)")
    plt.ylabel("Neer's Rating")
    plt.title("Win/Loss/Draw Classification")
    plt.show()

    return

def openings_performance(df):
    #Clean the dataframe of non-blitz games
    unwanted = ['bughousepartnerlose']
    df = df[~df['result'].isin(unwanted)]

    #Replace all the results with -1 for loss, 0 for draw, 1 for win
    df['result'] = df['result'].replace(['resigned', 'timeout', 'checkmated', 'abandoned'], -1)
    df['result'] = df['result'].replace(['agreed', 'insufficient', 'repetition', 'timevsinsufficient', 'stalemate', '50move'], 0)
    df['result'] = df['result'].replace('win', 1)

    #further clean data
    df = df.dropna(subset=['opening_name', 'result'])

    #Group by opening and calculate
    grouped = df.groupby('opening_name')
    games_played = grouped.size()
    win_rate  = grouped['result'].apply(lambda r: (r == 1).mean())
    tie_rate  = grouped['result'].apply(lambda r: (r == 0).mean())
    loss_rate = grouped['result'].apply(lambda r: (r == -1).mean())


    performance = pd.DataFrame({
        'games_played': games_played,
        'win_rate': win_rate,
        'tie_rate': tie_rate,
        'loss_rate': loss_rate
    })

    # Add play rate
    total_games = performance['games_played'].sum()
    performance['play_rate'] = performance['games_played'] / total_games

    # Sort by most played and filter by games (to avoid stupid amounts of data)
    performance = performance.sort_values('games_played', ascending=False)
    performance = performance[performance['games_played'] >= 10]

    #turn them into a percentage
    performance[['win_rate', 'tie_rate', 'loss_rate', 'play_rate']] *= 100
    performance = performance.round(2)


    #print(performance[['win_rate', 'loss_rate', 'tie_rate', 'play_rate']])
    #performance[['win_rate', 'loss_rate', 'tie_rate', 'play_rate']].to_csv('performance.csv', index=True)

    return performance[['win_rate', 'loss_rate', 'tie_rate', 'play_rate']]



def win_loss_draw_vs_other_features(df):
    #Clean the dataframe of non-blitz games
    unwanted = ['bughousepartnerlose']
    df = df[~df['result'].isin(unwanted)]

    #Replace all the results with -1 for loss, 0 for draw, 1 for win
    df['result'] = df['result'].replace(['resigned', 'timeout', 'checkmated', 'abandoned'], -1)
    df['result'] = df['result'].replace(['agreed', 'insufficient', 'repetition', 'timevsinsufficient', 'stalemate', '50move'], 0)
    df['result'] = df['result'].replace('win', 1)

    #replace 'played_as_color' with binary, white = 1 black = 0
    df['played_as_color'] = df['played_as_color'].replace({'black': 0, 'white': 1})

    #month
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    #calculations
    df['rating_diff'] = df['opponent_rating'] - df['rating_after_game']
    biggest_win = df['rating_diff'].max()
    biggest_loss = df['rating_diff'].min()
    print(f'Neerajs biggest win was against a player +{biggest_win} his elo.')
    print(f'Neerajs biggest loss was against a player {biggest_loss} his elo')
    print(df[df['rating_diff'] == biggest_loss])

    # Features & target (KEEP DRAWS)
    X = df[
        [
            'rating_diff',
            'rating_after_game',
            'opponent_rating',
            'duration_seconds',
            'played_as_color',
            'month',
            'year'
        ]
    ]
    y = df['result']
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Multinomial logistic regression
    model = LogisticRegression(
        multi_class='multinomial',
        solver='lbfgs',
        max_iter=1000
    )
    model.fit(X_scaled, y)

    class_names = {
    -1: 'Loss',
     0: 'Draw',
     1: 'Win'
    }

    for class_idx, class_label in zip(model.classes_, model.classes_):
        print(f"\n=== Coefficients for {class_names[class_label]} ===")
        coef_row = model.coef_[list(model.classes_).index(class_label)]
        for feature, weight in zip(X.columns, coef_row):
            print(f"{feature}: {weight:.4f}")