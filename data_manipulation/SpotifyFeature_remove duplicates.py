import pandas as pd
import collections

if __name__ == '__main__':
    df = pd.read_csv('./sources/raw_data/spotify_music/SpotifyFeatures0.csv')
    print(df.info)

    unique_pairs = set()
    pairs = []

    artists = df.artist_name
    songs = df.song_name

    print('len - artists:', len(artists), 'len - songs:', len(songs))

    for idx in range(0, len(artists)):
        pairs.append((artists[idx], songs[idx]))
        unique_pairs.add((artists[idx], songs[idx]))
    print('len - all pairs:', len(pairs), 'len - unique pairs:', len(unique_pairs))

    # list of duplicated items (so if [1, 1, 2] --> [1] since it is duplicated)
    duplicate_pairs = [item for item, count in collections.Counter(pairs).items() if count > 1]
    print('len - duplicate pairs:', len(duplicate_pairs))

    seen = set()
    uniq = [x for x in pairs if x in seen or seen.add(x)]
    print('len seen:', len(seen), 'len - uniq:', len(uniq))

    # list of duplicated songs, excluding the first one considered as the "original"
    songs_ids = []
    for item in duplicate_pairs:
        songs_id = list(df.loc[(df['artist_name'] == item[0]) & (df['song_name'] == item[1])].song_id)
        songs_ids.append(songs_id[1:len(songs_id)])

    print('len - songs_ids 1:', len(songs_ids))
    # [print(item) for item in songs_ids]

    songs_ids = [element for items in songs_ids for element in items]
    print('len - songs_ids 2:', len(songs_ids))
    # [print(item) for item in songs_ids]

    for song_id in songs_ids:
        df.drop(df[df.song_id == song_id].index, inplace=True)

    print(df.info)
    df.to_csv('./sources/processed_data/spotify_music/SpotifyFeatures.csv', index=False, encoding='utf-8')
