import pandas as pd

if __name__ == '__main__':

    path_file = r'./sources/raw_data/yahoo_music/txt/train_{0}.txt'
    output_file = r'./sources/raw_data/yahoo_music/Ratings0.csv'
    CHUNK_SIZE = 50000
    first_one = True

    for idx in range(0, 2):
        if not first_one:  # if it is not the first csv file then skip the header row (row 0) of that file
            skip_row = [0]
        else:
            skip_row = []

        chunk_container = pd.read_csv(path_file.format(idx), sep='\t', encoding='utf-8',
                                      chunksize=CHUNK_SIZE, skiprows=skip_row)

        for chunk in chunk_container:
            chunk.columns = ['user_id', 'song_id', 'ratings']
            chunk.astype(dtype={'user_id': int, 'song_id': int, 'ratings': int})
            chunk.to_csv(output_file, mode="a", index=False, encoding='utf-8')
        first_one = False
