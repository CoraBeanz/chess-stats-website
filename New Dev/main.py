import pandas as pd
from  file_opener import load_chess_data
from analysis import plot_blitz_rank_vs_date
from analysis import win_loss_result_vs_other_features
from analysis import win_loss_draw_vs_other_features

def main():
    df = load_chess_data('neer_chess_data.csv')  #load dataframe
    #plot_blitz_rank_vs_date(df)
    #win_loss_result_vs_other_features(df)
    win_loss_draw_vs_other_features(df)
if __name__ == "__main__":
    main()