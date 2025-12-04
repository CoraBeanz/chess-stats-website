import analysis
import file_opener

def main():
    df = file_opener.load_chess_data('neer_chess_data.csv')
    df = file_opener.unpack_pgn(df)
    analysis.plot_blitz_rank_vs_date(df)
    analysis.win_loss_result_vs_other_features(df)

if __name__ == "__main__":
    main()