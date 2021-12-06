import pandas as pd

if __name__ == '__main__':
    path_file = r'../sources/processed_data/spotify_music/SpotifyFeatures.csv'
    df_data = pd.read_csv(path_file, encoding='utf-8', sep=',', header=0)
    df_data['song_id'] = df_data.index
    df_data = df_data.astype({'song_id': str})
    df_data.info()
    path_file = r'../sources/processed_data/spotify_music/SpotifyFeatures.csv'
    df_data.to_csv(path_file, sep=',', header=True, mode='w', encoding='utf-8', index=False)
