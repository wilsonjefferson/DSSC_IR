import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from core.recommender_systems.RecommenderSystem import RecommenderSystem


class CoolStartRS(RecommenderSystem):
    """
        Implement the RecommenderSystem class, this class just need
        information on the songs and, through a "songs space" is able to
        give recommendation, considering the last song listened
        by the user.

        The recommendation is performed by means of K-NN with the cosine
        similarity as metric. N closest songs-points, to the last listened
        song-point, are recommended.

        Parameters
        ----------

    """

    def __init__(self):
        super().__init__(table_name='SONGS')
        self.rec_songs = {}
        self.columns_of_number_type = self.sql_handler.select_columns(table_name=self.table_name,
                                                                      data_types=['integer', 'double'])
        x = self.sql_handler.search(table_name=self.table_name, conditions=(self.columns_of_number_type, []))
        self.x = pd.DataFrame(data=x, columns=self.columns_of_number_type)

    def k_neighbors(self, current_user_id: str, current_song_id: str, n_songs: int, index: list, get_listened: bool):
        """
            Select n_songs from index row, under the condition if the already listened songs
            have to be considered or not.

            Parameters
            ----------
            current_user_id : ID of the logged user

            current_song_id : ID of the last listened song

            n_songs : number of songs to be recommended

            index : list of row index of the songs, ordered according the distances from current_song_id

            get_listened : if already listened songs have to be considered or not

            Returns
            -------
            rec_songs : list of recommended songs by ID
        """
        if get_listened:
            rec_songs = [self.get_vector(current_song_id)]
        else:
            rec_songs = {}
        counter, list_position = (0, 0)

        while list_position < len(index[1]) and counter < n_songs:
            idx = index[1][list_position]
            rec_song = self.sql_handler.search(self.table_name, (('song_id',), [('ROWID', '=', int(idx))]))
            if len(rec_song) != 0:
                rec_song_listened = self.sql_handler.search('HISTORY', (('song_id',),
                                                                        [('user_id', '=', current_user_id),
                                                                         'AND',
                                                                         ('song_id', '=', rec_song)]))

                if len(rec_song_listened) != 0:
                    rec_song_listened = rec_song == rec_song_listened

                if get_listened:
                    if rec_song_listened:
                        rec_songs.append(self.get_vector(rec_song))
                    counter += 1
                else:
                    if not rec_song_listened:
                        rec_songs[rec_song] = 1 - index[0][list_position]  # cosine similarity = 1 - cosine distance
                        counter += 1

            list_position += 1
        return rec_songs

    def get_vector(self, song_id: str):
        """
            Given a songID, this method provide the array of number features.

            Parameters
            ----------
            song_id : ID of the given song

            Returns
            -------
            array of features song
        """
        columns = self.sql_handler.columns_of(table_name=self.table_name)
        idx_columns_of_number_type = []
        for column in self.columns_of_number_type:
            idx_columns_of_number_type.append(columns.index(column))

        song_data = self.sql_handler.search(table_name=self.table_name,
                                            conditions=(('*',), [('song_id', '=', song_id)]))
        song_vector = []
        for idx in idx_columns_of_number_type:
            song_vector.append(song_data[idx])

        return np.array(song_vector)

    def recommend_songs(self, current_user_id: str, current_song_id: str, n_songs: int = 10):
        """
            Create a song space by their features, and apply KNN on the current song.
            The Algorithm follow this procedure:
            1. Select n_songs items closest to current_song_id
            2. Select from (1) already listened songs, current_song_id is part of this set
                2.1. If no how was already listened, then suggest them to the user
            3. Compute the 'artificial middle song' among songs from (2)
            4. Select the n_songs never listened items closest to the artificial song point
            5. Recommend items from (4)

            Parameters
            ----------
            current_user_id : ID of the logged user

            current_song_id : ID of the last listened song

            n_songs : number of songs to be recommended

            Returns
            -------
            rec_songs : list of recommended songs by ID
        """
        song_vector = self.get_vector(current_song_id)
        scaler = StandardScaler()
        scaler.fit(self.x)
        scaled_data = scaler.transform(self.x)
        scaled_song_vector = scaler.transform(song_vector.reshape(1, -1))
        neigh = NearestNeighbors(n_neighbors=10, metric='cosine', n_jobs=-1)
        neigh.fit(scaled_data)

        index = neigh.kneighbors(X=scaled_song_vector, n_neighbors=10, return_distance=True)
        index = [index[0][0].tolist(), index[1][0].tolist()]  # just for a better readability

        already_listened_songs_vectors = self.k_neighbors(current_user_id, current_song_id, n_songs, index, True)

        if len(already_listened_songs_vectors) > 1:
            listened_songs_matrix = np.array(already_listened_songs_vectors)
            listened_songs_mean_vector = np.mean(listened_songs_matrix, axis=0)

            array_comparison_bool_matrix = np.equal(self.x, listened_songs_mean_vector)  # matrix of bool

            # check if listened_songs_mean_vector is present in self.x as a vector row
            if True in np.apply_along_axis(lambda x: True if np.alltrue(x) else False, 1, array_comparison_bool_matrix):
                listened_mean_row = [(self.columns_of_number_type[idx], listened_songs_mean_vector[idx])
                                     for idx in range(0, len(listened_songs_mean_vector))]
                column_conditions = []
                for column_name, column_value in listened_mean_row:
                    condition = (column_name, '=', column_value)
                    column_conditions.append(condition)
                    column_conditions.append('AND')

                conditions = (('song_id',), column_conditions[:-1])
                mean_song_id = self.sql_handler.search(self.table_name, conditions)

                if mean_song_id and mean_song_id not in self.sql_handler.search('HISTORY',
                                                                                (('song_id',),
                                                                                 [('user_id', '=', current_user_id),
                                                                                  'AND',
                                                                                  ('song_id', '=', mean_song_id)])):
                    self.rec_songs[mean_song_id] = 1.0  # mean_song_id first recommendation
                    n_songs = n_songs - 1  # update number of items to find

            scaled_listened_songs_mean_vector = scaler.transform(listened_songs_mean_vector.reshape(1, -1))

            index = neigh.kneighbors(X=scaled_listened_songs_mean_vector, n_neighbors=scaled_data.shape[0],
                                     return_distance=True)
            index = [index[0][0].tolist(), index[1][0].tolist()]  # just for a better readability
            self.rec_songs.update(self.k_neighbors(current_user_id, current_song_id, n_songs, index, False))
        else:
            self.rec_songs = self.k_neighbors(current_user_id, current_song_id, n_songs, index, False)

        return self.rec_songs

    def __str__(self):
        return self.print('CoolStartRS', self.rec_songs) if self.rec_songs else ''
