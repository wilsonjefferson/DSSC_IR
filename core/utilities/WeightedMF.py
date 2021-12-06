import types

import numpy as np
import pandas as pd

from core.utilities.GeneralModel import GeneralModel
from core.utilities.WeightedALS import WeightedALS


class WeightedMF(GeneralModel):
    """
        This method implements the GeneralModel, and it implements
        the Weighted Matrix Factorization algorithm by means of WALS.

        Parameters
        ----------
        x : data matrix

        include_inner_biases : indicate if the bias associated with the rows
        columns has to be included in the Matrix Factorization

        custom_score_function : personalized score function (cost function)
    """

    def __init__(self, x: np.ndarray, include_inner_biases: bool = False,
                 custom_score_function: types.FunctionType = None):
        super().__init__()
        self.x = x
        self.predict_x = None
        self.latent_rows, self.latent_columns = (None, None)
        self.regularization = 0.0

        self.train_set, self.test_set = (self.x.copy(), self.x.copy())

        self.bias_rows_columns = 0.0
        self.bias_rows = np.zeros(shape=(self.train_set.shape[0], 1))  # M^(n_users, 1)
        self.bias_columns = np.zeros(shape=(1, self.train_set.shape[1]))  # M^(1, n_items)

        self.weight = np.ones(shape=self.train_set.shape)
        self.wals = None

        if include_inner_biases:
            self.bias_rows_columns = float(np.mean(a=self.train_set))
            bias_rows = np.reshape(np.mean(a=self.train_set, axis=1), newshape=(-1, 1))
            bias_columns = np.reshape(np.mean(a=self.train_set, axis=0), newshape=(1, -1))

            self.bias_rows = (-1.0) * (self.bias_rows_columns - bias_rows)
            self.bias_columns = (-1.0) * (self.bias_rows_columns - bias_columns)

        self.score = self.score if custom_score_function is None else custom_score_function

    def fit(self, regularization: float, n_iteration: int, n_latent_factors: int,
            weight: np.ndarray = None, split_wals: bool = False, weighted_mf_score_function: bool = False):
        """
            Method to fit the WMF model, in particular here we call an instance of the WALS class with the
            constrain to split the original dataset if it is required. WALS provide the embeddings matrices,
            used to re-compute an approximated version of the original matrix.

            Parameters
            ----------
            regularization : it's the regularization parameter

            n_iteration : number of iteration

            n_latent_factors : number of latent factors of the embeddings matrices

            weight : the associated weight matrix to the given dataset

            split_wals : binary variable to decide if the dataset should be splitted or not

            weighted_mf_score_function : use score function of this class if True, use the WALS score function otherwise

            Returns
            -------
            Nothing
        """
        self.regularization = regularization
        self.weight = self.weight if weight is None else weight

        score_function = self.score if weighted_mf_score_function else None

        self.wals = WeightedALS(self.train_set, regularization, n_iteration, n_latent_factors, self.weight,
                                self.bias_rows_columns, self.bias_rows, self.bias_columns, score_function)

        if split_wals:
            self.wals.split()  # split wals.x in train_set and test_set (used for plotting MSE)

        self.latent_rows, self.latent_columns = self.wals.fit()  # M^(n_users, n_latent_factors), M^(n_items, n_latent_factors)

        # R_aprx = bias + bias_u + bias_v + U * V.T
        self.predict_x = self.bias_rows_columns + self.bias_rows + \
                         self.bias_columns + self.latent_rows.dot(self.latent_columns.T)

    def score(self, test_set: np.array = None, latent_rows: np.array = None, latent_columns: np.array = None,
              regularization: float = None, weight: np.array = None, bias_rows_columns: float = None,
              bias_rows: np.array = None, bias_columns: np.array = None):
        """
            Compute the score of the Weighted Matrix Factorization with the computed embedded matrices.

            Parameters
            ----------


            Returns
            -------
            Score value
        """
        test_set = self.test_set if test_set is None else test_set
        latent_rows = self.latent_rows if latent_rows is None else latent_rows
        latent_columns = self.latent_columns if latent_columns is None else latent_columns
        regularization = self.regularization if regularization is None else regularization
        weight = self.weight if weight is None else weight
        bias_rows_columns = self.bias_rows_columns if bias_rows_columns is None else bias_rows_columns
        bias_rows = self.bias_rows if bias_rows is None else bias_rows
        bias_columns = self.bias_columns if bias_columns is None else bias_columns

        # R - U * V.T
        a = test_set - latent_rows.dot(latent_columns.T)

        # R - bias - bias_u - bias_v - U * V.T
        a = a - (bias_rows_columns + bias_rows + bias_columns)

        # W @ (R - bias - bias_u - bias_v - U * V.T)
        a = np.multiply(weight, a)

        # || W @ (R - bias - bias_u - bias_v - U * V.T) || ** 2
        a = np.linalg.norm(a) ** 2

        # reg * (|| U || ** 2 + || V || ** 2 + bias_u ** 2 + bias_v ** 2)
        b = np.matrix.trace(np.linalg.norm(latent_rows, axis=1) ** 2 + bias_rows ** 2)
        b += np.matrix.trace(np.linalg.norm(latent_columns, axis=1) ** 2 + bias_columns ** 2)
        b *= regularization

        # || W @ (R - bias - bias_u - bias_v - U * V.T) || ** 2 + reg * (|| U || ** 2 + || V || ** 2 + bias_u ** 2 + bias_v ** 2)
        return a + b

    def plot_wals_mse(self):
        """
            Method to plot the WALS MSE.

            Parameters
            ----------


            Returns
            -------
            Nothing
        """
        self.wals.plot()


if __name__ == '__main__':
    np.random.seed(0)
    n_users, n_items = (100, 1000)
    data = np.random.randint(low=0, high=6, size=(n_users, n_items))
    n_iter = 100
    reg = 0.05
    n_factors = 50

    df = pd.read_csv(filepath_or_buffer=r'../../sources/raw_data/yahoo_music/Ratings0.csv', sep=',', nrows=50000)
    data = df.pivot_table(index="user_id", columns="song_id", values="ratings", dropna=False, fill_value=0)
    data = data.values
    w = np.ones(shape=data.shape)

    wmf = WeightedMF(x=data, include_inner_biases=False)
    wmf.fit(reg, n_iter, n_factors, w, split_wals=False, weighted_mf_score_function=True)
    wmf.plot_wals_mse()
    print('Loss(R, U, V, bias, b_u, b_v, reg):', wmf.score())
