import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from core.recommender_systems.RecommenderSystem import RecommenderSystem
from exceptions.recommender_system.recommender_system_warning.RSNotValidInputWarning import RSNotValidInputWarning
from exceptions.recommender_system.recommender_system_warning.RSWarning import RSWarning


class UserBasedRS(RecommenderSystem):
    """
        Implement the RecommenderSystem class, this class just need
        information on the History of the users. It performs
        a Collaborative Analysis to provide a recommendation.

        The recommender system suggests N songs with higher score
        on songs never listened by the current user.

        P.s. This class does not implement any self.load() function
        because History should have an high update rate, so it does
        not make sense to load a csv that will be, for sure, already
        obsolete.

        Parameters
        ----------

    """

    def __init__(self):
        super().__init__('HISTORY')
        self.df_occurrences = None

        self.columns_of_number_type = self.sql_handler.select_columns(table_name='SONGS',
                                                                      data_types=['integer', 'double'])
        x = self.sql_handler.search(table_name='SONGS', conditions=(self.columns_of_number_type, []))
        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        songs_id = self.sql_handler.search(table_name='SONGS', conditions=(('song_id',), []))
        x_scaled = np.append(songs_id, x_scaled, axis=1)

        self.songs = pd.DataFrame(data=x_scaled, columns=['song_id'] + self.columns_of_number_type)
        self.rec_songs = None

    def create_dataframe(self, current_song_id: str):
        """
            Create the ratings dataframe from the ratings matrix.

            Parameters
            ----------
            current_song_id : ID of the song listened by the user

            Returns
            -------
            Ratings dataframe
        """
        df_occurrences = pd.DataFrame()
        if self.sql_handler.exist(self.table_name):
            df_occurrences = pd.DataFrame(self.sql_handler.search(sql='SELECT * FROM ' + self.table_name, flat=False))
            df_occurrences.columns = self.sql_handler.columns_of(self.table_name)
            df_occurrences.astype(dtype={'user_id': str, 'song_id': str}, copy=False)
            df_occurrences = df_occurrences.pivot_table(index='user_id', columns='song_id',
                                                        values='repetition',
                                                        dropna=False, fill_value=0)
            df_occurrences = df_occurrences[df_occurrences[current_song_id] != '0']

        return df_occurrences

    def history_per_user(self):
        """
            Create the dictionary of users id with their list of listened songs.

            Parameters
            ----------


            Returns
            -------
            users_songs_id_dict : the users and their listened songs
        """
        columns_names_vector = self.df_occurrences.columns.values  # vector of column names
        no_zero_mask = self.df_occurrences.gt(0).values  # np.array of bool to no-zero values in dataframe
        # list of lists of no-zero column names for each rows in dataframe
        no_zero_columns_names = [columns_names_vector[x].tolist() for x in no_zero_mask]
        # {user_id: no_zero_columns_names}
        users_songs_id_dict = dict(zip(self.df_occurrences.index.values, no_zero_columns_names))

        return users_songs_id_dict

    def build_songs_matrix_per_users(self, songs: pd.DataFrame, users_songs_history: dict):
        """
            Create the dictionary of users id with their matrix of listened features songs.

            Parameters
            ----------
            songs : dataframe of features songs

            users_songs_history : dictionary of users with their list of listened songs id

            Returns
            -------
            users_songs_matrix_dict : the users and their feature songs matrix
        """
        # {user_id: songs_matrix}
        users_songs_matrix_dict = {user_id: songs.loc[songs['song_id'].isin(songs_id)].
                                                loc[:, songs.columns != 'song_id'].to_numpy(dtype=float)
                                   for user_id, songs_id in users_songs_history.items()}

        return users_songs_matrix_dict

    def build_weights_dict_per_users(self):
        """
            Create the dictionary of users id with their vector of "weights" (i.e. repetition).
            Weight vector for each user is normalized considering the vector itself.

            Parameters
            ----------

            Returns
            -------
            dictionary : the users and their weight vector
        """
        weights_vectors = list()
        for idx, row in self.df_occurrences.iterrows():
            weight_vector = list()
            for repetition in row:
                if repetition:
                    weight_vector.append(repetition)

            weight_vector = [float(weight) / sum(weight_vector) for weight in weight_vector]  # normalization
            weights_vectors.append(np.reshape(np.array(weight_vector), (len(weight_vector), 1)))

        return dict(zip(self.df_occurrences.index, weights_vectors))

    def compute_centroid(self, songs_matrix: np.array, weight_vector: np.array):
        """
            Compute centroid vector from the matrix of songs features.

            Parameters
            ----------
            songs_matrix : matrix of features of songs

            weight_vector : vector of weights for each feature vector song

            Returns
            -------
            np.array : centroid vector
        """
        return np.sum(songs_matrix * weight_vector, axis=0) / songs_matrix.shape[0]

    def compute_similarity(self, current_user_songs_vector: np.array, songs_dict: dict):
        """
            Compute similarities between a specific vector and a matrix of vectors.

            Parameters
            ----------
            current_user_songs_vector : target vector

            songs_dict : dictionary of users with their centroid vector

            Returns
            -------
            similarity_dict : the users with the distance of their centroid to the target vector
        """
        shape = [len(songs_dict.keys()), current_user_songs_vector.shape[1]]
        users_centroids_matrix = np.array(np.array(list(songs_dict.values()), dtype=object))
        users_centroids_matrix = np.concatenate(users_centroids_matrix).reshape(shape)

        similarity_vector = cosine_similarity(current_user_songs_vector, users_centroids_matrix)[0]
        similarity_dict = dict(zip(list(songs_dict.keys()), similarity_vector))
        similarity_dict = dict(sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True))  # descending ordering
        return similarity_dict

    def k_neighbors(self, songs: pd.DataFrame, songs_repetition_dict: dict, listened_song_id: str,
                    n_songs: [int, None]):
        """
            Compute KNN between the listened song and set of songs not listened by
            the current user and that are considered valid to be recommended. This
            method compute the distances and select the n closest songs.

            Parameters
            ----------
            songs : songs feature dataframe

            songs_repetition_dict : dictionary of valid songs and number of users have listened them

            listened_song_id : id of the listened song from the current user

            n_songs : number of songs to consider in KNN

            Returns
            -------
            closest_songs_to_listened_song : list of distances and song index position in songs_matrix
        """
        # build matrix of valid songs
        songs_matrix = songs[songs['song_id'].isin(songs_repetition_dict.keys())]
        songs_matrix = songs_matrix.loc[:, songs_matrix.columns != 'song_id'].to_numpy(dtype=float)

        # build vector of the listened song
        listened_song_vector = songs[songs['song_id'] == listened_song_id]
        listened_song_vector = listened_song_vector.loc[:, listened_song_vector.columns != 'song_id'].to_numpy(
            dtype=float)

        n_songs = n_songs if n_songs is not None else songs_matrix.shape[0]

        neigh = NearestNeighbors(n_neighbors=n_songs, metric='cosine', n_jobs=-1)
        neigh.fit(songs_matrix)

        # compute distances between listened song and all the valid songs
        closest_songs_to_listened_song = neigh.kneighbors(X=listened_song_vector, return_distance=True)
        closest_songs_to_listened_song = [closest_songs_to_listened_song[0][0].tolist(),
                                          closest_songs_to_listened_song[1][
                                              0].tolist()]  # just for a better readability

        return closest_songs_to_listened_song

    def sample_recommendation(self, closest_songs_to_listened_song: dict, songs_repetition_dict: dict,
                              sample_mode: str, n_songs: int = None):
        """
            From the closest songs to the listened song, sample n_songs to be suggested to the current user.

            Parameters
            ----------
            closest_songs_to_listened_song : dictionary of closest songs and their distance

            songs_repetition_dict : dictionary of valid songs and number of users have listened them

            sample_mode : type of sampling (TopN, Uniform, Distribution)

            n_songs : number of closest songs to select

            Returns
            -------
            sample_closest_songs : dictionary of recommended songs and their score
        """
        # consider random sample instead of selecting closest n_songs by using repetition in songs_repetition_dict
        if sample_mode == 'TopN' and n_songs:
            return dict(list(closest_songs_to_listened_song.items())[:n_songs + 1])

        if n_songs < len(closest_songs_to_listened_song):
            n_songs = n_songs
        elif n_songs == len(closest_songs_to_listened_song):
            n_songs -= 1
        elif n_songs > len(closest_songs_to_listened_song):
            RSWarning("{} recommender: {} is not a valid input, more than the valid songs!".format('UserBasedRS', n_songs))
            n_songs = len(closest_songs_to_listened_song) - 1

        if sample_mode == 'Uniform':
            sample_weights = [1 / len(closest_songs_to_listened_song)] * len(closest_songs_to_listened_song)
            sample_songs = np.random.choice(list(closest_songs_to_listened_song.keys()),
                                            size=n_songs, replace=False,
                                            p=sample_weights)

            # {selected song : distance}
            return {song_id: closest_songs_to_listened_song[song_id] for song_id in sample_songs}
        elif sample_mode == 'Distribution':
            # sampling of songs positions according their repetition-frequency

            # songs_repetition_dict contains all the songs listened by the users,
            # also the songs listened by the current user, these are removed
            songs_repetition_dict = {song_rep_id: repetition for song_rep_id, repetition in
                                     songs_repetition_dict.items()
                                     if song_rep_id in closest_songs_to_listened_song.keys()}
            self.print_dict('filter songs_repetition according closest songs', songs_repetition_dict)
            self.print_dict('closest songs to listened with similarity', closest_songs_to_listened_song)

            # sample songs according their repetition
            # compute sample weights as repetition * similarity distance
            sample_weights = []
            for song_id in closest_songs_to_listened_song.keys():
                sample_weights.append(closest_songs_to_listened_song[song_id] * songs_repetition_dict[song_id])

            # MaxMin Scaling to bring weights in [0, 1]
            sample_weights = (sample_weights - np.min(sample_weights)) / (
                        np.max(sample_weights) - np.min(sample_weights))
            sample_weights /= np.sum(sample_weights)  # Normalize to sum to 1 the weights

            sample_songs = np.random.choice(list(songs_repetition_dict.keys()),
                                            size=n_songs, replace=False, p=sample_weights)

            # {selected song : distance}
            return {song_id: closest_songs_to_listened_song[song_id] for song_id in sample_songs}
        else:
            RSNotValidInputWarning('UserBasedRS', sample_mode, False)
            return closest_songs_to_listened_song

    def no_other_items(self, dictionary: dict, key: str = None):
        if key:
            keys = list(dictionary.keys())
            keys.pop(int(key))
            return len(keys) == 0
        else:
            return len(dictionary) <= 0

    def recommend_songs(self, current_user_id: str, listened_song_id: str, n_songs: int = 10,
                        sample_mode: str = 'TopN', local_neighbors: bool = True):
        """
            Main function to recommend n_songs to the user according the UserBasedRS algorithm.
            This algorithm follow this procedure:
            1. From users history, select those that present the listened song
            2. For each user, compute the centroid vector from the feature songs dataframe for their listened songs
            3. Select n closest users to the current user according the distances from the current user
               centroid and the centroids of the other users
            4. For each user, consider just songs that are never listened by the current user from their listened songs
               and compute KNN between the listened song feature vector and these remained songs
            5. Pick the closest n and recommend them to the user

            P.s. In step 2 we have defined clusters of songs, each clusters represent a certain user

            Parameters
            ----------
            current_user_id : songs feature dataframe

            listened_song_id : dictionary of valid songs and number of users have listened them

            n_songs : number of songs to be suggested

            sample_mode : type of song sampling to execute

            local_neighbors : Consider n_songs if True, otherwise consider all "valid" songs

            Returns
            -------
            rec_songs : dictionary of recommended songs and their score
        """
        # gather similar users according history to the current user
        self.df_occurrences = self.create_dataframe(listened_song_id)
        songs = self.songs[self.songs['song_id'].isin(self.df_occurrences.columns)]

        self.print_dict('gather similar users according history to the current user', songs)

        # take N most similar users
        # For each users provide their history songs id
        users_songs_id_dict = self.history_per_user()

        if self.no_other_items(dictionary=users_songs_id_dict, key=current_user_id):
            RSWarning('There are no other users in HISTORY, apart for the current user {0}'.format(current_user_id))
            return {}

        self.print_dict('For each users provide their history songs id', users_songs_id_dict)

        # For each users provide their songs features matrix
        users_songs_matrix_dict = self.build_songs_matrix_per_users(songs, users_songs_id_dict)

        self.print_dict('For each users provide their songs features matrix', users_songs_matrix_dict)

        # For each users provide their weights matrix
        weights_dict = self.build_weights_dict_per_users()

        self.print_dict('For each users provide their weights matrix', weights_dict)

        # For each users provide their centroid vector
        centroids_dict = {user_id: self.compute_centroid(users_songs_matrix_dict[user_id], weights_dict[user_id])
                          for user_id in users_songs_id_dict.keys()}

        self.print_dict('For each users provide their centroid vector', centroids_dict)

        current_user_centroid = centroids_dict.get(current_user_id)
        current_user_centroid = np.reshape(current_user_centroid, (1, current_user_centroid.shape[0]))
        centroids_dict.pop(current_user_id)  # remove target centroid from the set of centroids

        # For each users provide their similarity distance to the current user
        similarity_dict = self.compute_similarity(current_user_centroid, centroids_dict)

        self.print_dict('For each users provide their similarity distance to the current user', similarity_dict)

        # remove users not so similar with the current user
        for idx, user_id in enumerate(list(similarity_dict.keys())):
            if idx > n_songs:
                users_songs_id_dict.pop(user_id)
                weights_dict.pop(user_id)
                centroids_dict.pop(user_id)
                users_songs_matrix_dict.pop(user_id)
                similarity_dict.pop(user_id)

        # from each users, gather all the songs never listened by the current user
        current_user_songs_id = users_songs_id_dict.get(current_user_id)
        users_songs_id_dict.pop(current_user_id)

        # build a dict containing all songs id from the top N most similar users to current_user
        # For each valid song provide their repetition
        songs_repetition_dict = dict()  # {song_id : repetition}
        for user_id, songs_id in users_songs_id_dict.items():
            valid_songs = [song_id for song_id in songs_id
                           if song_id not in current_user_songs_id]

            for song_id in valid_songs:
                if song_id not in songs_repetition_dict.keys():
                    songs_repetition_dict[song_id] = 1
                else:
                    songs_repetition_dict[song_id] += 1

        if self.no_other_items(songs_repetition_dict):
            RSWarning('There are no valid songs from the other users')
            return {}

        self.print_dict('For each valid song provide their repetition', songs_repetition_dict)

        # list of distances and position of the valid song --> [[distances], [indexes]]
        k_nsongs = n_songs if local_neighbors else None
        closest_songs_to_listened_song = self.k_neighbors(songs, songs_repetition_dict, listened_song_id, k_nsongs)

        # list n_songs of selected valid songs id
        valid_songs_id = map(list(songs_repetition_dict.keys()).__getitem__, closest_songs_to_listened_song[1])

        # {song_id : cosine similarity measure with the listened song}
        closest_songs_to_listened_song = dict(zip(valid_songs_id, np.ones(len(closest_songs_to_listened_song[0]))
                                                  - closest_songs_to_listened_song[0]))

        self.print_dict('closest songs to listened with similarity', closest_songs_to_listened_song)

        # sample n_songs from closest_songs_to_listened_song according a sample mode
        closest_songs_to_listened_song = self.sample_recommendation(closest_songs_to_listened_song,
                                                                    songs_repetition_dict, sample_mode, n_songs)

        self.print_dict('sample n_songs from closest_songs_to_listened_song according a sample mode',
                        closest_songs_to_listened_song)

        # sort dictionary according similarity measures
        self.rec_songs = dict(sorted(closest_songs_to_listened_song.items(), key=lambda item: item[1], reverse=True))

        # suggest 10 most similar songs to current song
        return self.rec_songs

    def __str__(self):
        return self.print('UserBasedRS', self.rec_songs) if self.rec_songs else ''

    def print_dict(self, title: str, dictionary: dict, ignore: bool = True):
        if not ignore:
            print(title)
            for key, value in dictionary.items():
                print(key, value)


if __name__ == '__main__':
    user_based_rs = UserBasedRS()
    user = '0'
    song = '2245'
    user_based_rs.recommend_songs(user, song)
    print(user_based_rs)
