import pandas as pd

def load_chess_data(filepath):
    df = pd.read_csv(filepath)
    print(df.head()) 
    return df

#Expands the df with several new series of pgn data it has extracted
def unpack_pgn(df):
    #Extract Date from pgn and clean dataset
    df['date'] = df['pgn'].str.extract(r'\[Date\s+"(\d{4}\.\d{2}\.\d{2})"\]', expand=False)
    df['date'] = df['date'].fillna(df['pgn'].str.extract(r'\[UTCDate\s+"(\d{4}\.\d{2}\.\d{2})"\]', expand=False))
    df['date'] = pd.to_datetime(df['date'], format='%Y.%m.%d', errors='coerce')
    df = df.dropna(subset=['date'])

    #Extract ECO from pgn and clean dataset
    df['ECO'] = df['pgn'].str.extract(r'\[ECO\s+"(.*?)"\]')
    df = df.dropna(subset=['ECO'])

    #Extract opening names from pgn
    df['opening_name'] = df['pgn'].str.extract(r'\[ECOUrl\s+".*/openings/(.*?)"\]', expand=False)
    #df[['opening_name']].to_csv('opening_name.csv', index=False)

    return df

# Example usage
if __name__ == "__main__":
    # Adjust the path to your CSV file
    data = load_chess_data('neer_chess_data.csv')


