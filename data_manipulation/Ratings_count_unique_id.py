import csv


if __name__ == '__main__':
    path_file = r'./sources/raw_data/yahoo_music/Ratings0.csv'

    max_min = {}
    max_user_id, min_user_id = (None, None)
    max_song_id, min_song_id = (None, None)
    columns = ['user_id', 'song_id']

    with open(file=path_file, mode='r', encoding='utf-8', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            user_id, song_id = (row[0], row[1])

            if user_id != 'user_id' and song_id != 'song_id':
                user_id = int(user_id)
                song_id = int(song_id)

                if max_user_id is None:
                    max_user_id = user_id
                elif max_user_id < user_id:
                    max_user_id = user_id

                if min_user_id is None:
                    min_user_id = user_id
                elif min_user_id > user_id:
                    min_user_id = user_id

                if max_song_id is None:
                    max_song_id = song_id
                elif max_song_id < song_id:
                    max_song_id = song_id

                if min_song_id is None:
                    min_song_id = song_id
                elif min_song_id > song_id:
                    min_song_id = song_id

    max_min['user_id'] = [max_user_id, min_user_id]
    max_min['song_id'] = [max_song_id, min_song_id]

    print('user_id - max:', max_min['user_id'][0], 'min:', max_min['user_id'][1])
    print('song_id - max:', max_min['song_id'][0], 'min:', max_min['song_id'][1])

    # user_id - max: 399999 min: 0
    # song_id - max: 136735 min: 0
