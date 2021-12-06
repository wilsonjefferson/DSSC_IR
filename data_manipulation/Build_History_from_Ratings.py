import pandas as pd
from pandas import RangeIndex

from core.data_handlers.HistoryTable import HistoryTable


if __name__ == '__main__':
    history = HistoryTable()

    input_file = r'../sources/processed_data/yahoo_music/Ratings.csv'
    output_file = r'../sources/History.csv'
    CHUNK_SIZE = 1000

    chunk_container = pd.read_csv(input_file, sep=',', encoding='utf-8',
                                  chunksize=CHUNK_SIZE,
                                  header=0, usecols=['user_id', 'song_id'],
                                  dtype={'user_id': str, 'song_id': str})

    for chunk in chunk_container:
        chunk.index = RangeIndex(len(chunk))
        for idx in chunk.index:
            user_id, song_id = chunk.iloc[idx]
            history.add(user_id, song_id)

    history.store_csv(path_file=output_file, separator=',')
