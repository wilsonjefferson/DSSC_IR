import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize
from core.utilities.HyperTuner import HyperTuner
from core.utilities.WeightedMF import WeightedMF
from core.recommender_systems.RecommenderSystem import RecommenderSystem
from exceptions.input_validation.input_validation_warning.InputValidationWarning import InputNotFoundWarning


class WeightedMFBasedRS(RecommenderSystem):
    """
        Implement the RecommenderSystem class, this class just need
        information on the rating that users give to songs. It performs
        a Weighted Matrix Factorization (WMF), by means of Weighted
        Alternate Least Square Algorithm (WALS).

        The recommender system suggests N songs with higher approximated
        ratings on songs never listened by the user.

        Parameters
        ----------
        path_file : path where the Ratings user-song is stored

        separator : considered separator for the csv file

        weight : matrix of weights related to each user-song pair

        regularization_range : range for regularization hyperparameter

        n_latent_factors_range : range for number of latent factors hyperparameter

        n_iteration_range : range for number of iteration hyperparameter

        regularization : regularization hyperparameter given in input

        n_latent_factors : number of latent factors hyperparameter given in input

        n_iteration : number of iteration hyperparameter given in input
    """

    def __init__(self, path_file: str = None, separator: str = None, weight: np.ndarray = None,
                 regularization_range: tuple = None, n_latent_factors_range: tuple = None,
                 n_iteration_range: tuple = None, regularization: float = None, n_latent_factors: int = None,
                 n_iteration: int = None):
        super().__init__('RATINGS')
        self.rec_songs = {}
        self.df_ratings = self.create_dataframe(path_file=path_file, separator=separator)
        ratings = self.df_ratings.to_numpy()
        self.df_predicted_ratings = self.create_dataframe(
            data_matrix=self.factorization(data_matrix=ratings,
                                           weight=weight, skip_opt=True,
                                           regularization_range=regularization_range,
                                           n_latent_factors_range=n_latent_factors_range,
                                           n_iteration_range=n_iteration_range,
                                           regularization=regularization,
                                           n_latent_factors=n_latent_factors,
                                           n_iteration=n_iteration))

    def factorization(self, data_matrix: np.ndarray, weight: np.ndarray = None,
                      regularization_range: tuple = (0.01, 1.0), n_latent_factors_range: tuple = (20, 60),
                      n_iteration_range: tuple = (100, 120),
                      regularization: float = None, n_latent_factors: int = None,
                      n_iteration: int = None,
                      skip_opt: bool = False, include_inner_biases: bool = True,
                      split_wals: bool = False, weighted_mf_score_function: bool = True,
                      plot_wals_mse: bool = False):
        """
            Main method of the Weighted Matrix Factorization procedure. Before the
            factorization a Bayesian Optimizer is used to tune the hyperparameters
            of the WMF (regularization term, number of latent factors and number of iteration).
            With the tuned hyperparameters a WMF model if fitted on the ratings matrix.

            Parameters
            ----------
            data_matrix : ratings, that is the explicit feedback matrix

            weight : a matrix with weights for each user-item interaction

            regularization_range : range for regularization hyperparameter

            n_latent_factors_range : range for number of latent factors hyperparameter

            n_iteration_range : range for number of iteration hyperparameter

            regularization : regularization hyperparameter

            n_latent_factors : number of latent factors hyperparameter

            n_iteration : number of iteration hyperparameter

            skip_opt : skip Bayesian Optimization if True, otherwise don't skip it

            include_inner_biases : include inner biases if True, otherwise don't include them

            split_wals : split data_matrix in train and test set to compute MSE-score, otherwise don't split it

            weighted_mf_score_function : use WeightedMF score function as MSE-score function, otherwise use MSE

            plot_wals_mse : pot WALS MSE if True, otherwise don't plot it

            Returns
            -------
            wmf.predict_x : the approximated ratings matrix
        """

        # if Bayesian Optimization was skipped, default empirical values are considered
        if skip_opt:
            valid_hyperparameters = True
            if regularization is None:
                InputNotFoundWarning('regularization', regularization, False)
                valid_hyperparameters = False

            if n_latent_factors is None:
                InputNotFoundWarning('n_latent_factors', n_latent_factors, False)
                valid_hyperparameters = False

            if n_iteration is None:
                InputNotFoundWarning('n_iteration', n_iteration, False)
                valid_hyperparameters = False

            if not valid_hyperparameters:
                return None
            else:
                tuned_regularization = regularization
                tuned_n_latent_factors = n_latent_factors
                tuned_n_iteration = n_iteration

        else:
            optimizer = HyperTuner(x=data_matrix, object_class=WeightedMF,
                                   pbounds={'regularization': regularization_range,
                                            'n_latent_factors': n_latent_factors_range,
                                            'n_iteration': n_iteration_range},
                                   random_state=1,
                                   bounds_transformer=None,
                                   max_opt=False, verbose=2)

            optimizer.maximize(init_points=20, n_iter=5)

            tuned_regularization = optimizer.max['params']['regularization']
            tuned_n_latent_factors = int(optimizer.max['params']['n_latent_factors'])
            tuned_n_iteration = int(optimizer.max['params']['n_iteration'])

        wmf = WeightedMF(x=data_matrix, include_inner_biases=include_inner_biases)
        wmf.fit(tuned_regularization, tuned_n_iteration, tuned_n_latent_factors, weight,
                split_wals=split_wals, weighted_mf_score_function=weighted_mf_score_function)

        # include_inner_biases=False, split_wals=False, weighted_mf_score_function=False
        # include_inner_biases=False, split_wals=False, weighted_mf_score_function=True
        # include_inner_biases=False, split_wals=True, weighted_mf_score_function=False
        # include_inner_biases=False, split_wals=True, weighted_mf_score_function=True

        # include_inner_biases=True, split_wals=False, weighted_mf_score_function=False
        # include_inner_biases=True, split_wals=False, weighted_mf_score_function=True
        # include_inner_biases=True, split_wals=True, weighted_mf_score_function=False
        # include_inner_biases=True, split_wals=True, weighted_mf_score_function=True

        if plot_wals_mse:
            wmf.plot_wals_mse()

        return wmf.predict_x

    def load(self, path_file: str, separator: str = '\t', n_rows: int = 50000):
        """
            Load the csv ratings file from the given position.

            Parameters
            ----------
            path_file : path where from load the ratings csv file

            separator : considered separator for the csv file

            n_rows : how many rows read from csv

            Returns
            -------
            Ratings dataframe
        """
        return pd.read_csv(filepath_or_buffer=path_file, sep=separator, nrows=n_rows)

    def store(self, path_file: str, separator: str = '\t'):
        """
            Store the ratings dataframe in the given position, in csv format.

            Parameters
            ----------
            path_file : path where to store the ratings dataframe

            separator : considered separator for the csv file

            Returns
            -------
            Nothing
        """
        self.df_ratings.to_csv(path_file, sep=separator, mode='w', encoding='utf-8')

    def create_dataframe(self, path_file: str = None, separator: str = None, data_matrix: np.ndarray = None):
        """
            Create the ratings dataframe from the ratings matrix.

            Parameters
            ----------
            path_file : path where find the csv file

            separator : considered separator for the csv file

            data_matrix : ratings matrix without head and index

            Returns
            -------
            Ratings dataframe
        """
        if path_file is None and data_matrix is None:
            df_ratings = pd.DataFrame(self.sql_handler.search(sql='SELECT * FROM ' + self.table_name, flat=False))
            df_ratings.columns = self.sql_handler.columns_of(self.table_name)
            df_ratings = df_ratings.pivot_table(index='user_id', columns='song_id',
                                                values='ratings',
                                                dropna=False, fill_value=0)
        elif path_file and data_matrix is None:
            df_ratings = self.load(path_file, separator=separator).pivot_table(index='user_id', columns='song_id',
                                                                               values='ratings',
                                                                               dropna=False, fill_value=0)
        else:
            df_ratings = pd.DataFrame(data_matrix)
            df_ratings.columns = list(map(str, self.df_ratings.columns))  # columns are strings
            df_ratings.index = list(map(str, self.df_ratings.index))  # indexes are strings

        return df_ratings

    def recommend_songs(self, current_user_id: str, n_songs: int = 10):
        """
            Recommend n_songs to the current user by means of Weighted Matrix
            Factorization over the user-item ratings matrix.

            Parameters
            ----------
            current_user_id : ID of the logged user

            n_songs : number of songs to be recommended

            Returns
            -------
            list of the recommended n_songs
        """

        if self.df_predicted_ratings is not None:
            normalized_predicted_ratings = normalize(self.df_predicted_ratings, norm='max')
            df_normalized_predicted_ratings = pd.DataFrame(normalized_predicted_ratings,
                                                           columns=self.df_predicted_ratings.columns,
                                                           index=self.df_predicted_ratings.index)

            predicted_current_user_ratings = list(df_normalized_predicted_ratings.loc[current_user_id, :])
            predicted_current_user_ratings = np.array(predicted_current_user_ratings)

            # get n_songs scores in descending order
            predicted_songs_scores = np.sort(predicted_current_user_ratings)[::-1][:n_songs]
            # get n_songs_song_id in descending order (in respect the n_songs scores in descending order)
            predicted_songs_id = df_normalized_predicted_ratings.columns[
                predicted_current_user_ratings.argsort()[::-1][:n_songs]]

            self.rec_songs = dict(zip(predicted_songs_id, predicted_songs_scores))  # dictionary {song_id : normalized_value}

        return self.rec_songs

    def __str__(self):
        return self.print('WeightedMFBasedRS', self.rec_songs) if self.rec_songs else ''
