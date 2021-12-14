import types

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from core.utilities.GeneralModel import GeneralModel


class WeightedALS(GeneralModel):
    """
        This class implements the GeneralModel class, and it performs
        the Weighted Alternative Least Square algorithm: the embedded
        matrices are constructed by means of a given data matrix. Then,
        the data matrix is approximated, and where there were zero values,
        now a potential value is given.

        Parameters
        ----------
        x : data matrix

        regularization : lambda value

        n_iteration : number of iteration to construct the embedded matrices

        n_latent_factors : one of the dimension of the embedded matrices

        weight : weight matrix associated with the data matrix x

        bias_rows_columns : overall mean value on data matrix x

        bias_rows : mean for each row of the data matrix x, column vector

        bias_columns : mean for each column of the data matrix x, row vector
    """

    def __init__(self, x: np.ndarray, regularization: float, n_iteration: int, n_latent_factors: int,
                 weight: np.ndarray, bias_rows_columns: float, bias_rows: np.ndarray, bias_columns: np.ndarray,
                 custom_score_function: types.FunctionType = None):
        super().__init__()
        self.regularization = regularization
        self.n_iteration = int(n_iteration)
        self.n_latent_factors = int(n_latent_factors)
        self.x = x
        self.weight = weight
        self.train_set, self.test_set = (x.copy(), x.copy())

        self.bias_rows_columns = bias_rows_columns
        self.bias_rows = bias_rows
        self.bias_columns = bias_columns

        self.u = None
        self.v = None

        self.train_mse_record = []
        self.test_mse_record = []
        self.test_cost_function = []

        self.custom_score_function = None if custom_score_function is None else custom_score_function

    def fit(self):
        """
            This method iteratively compute the embedding matrices from the given
            dataset. At each step, the MSE is computed.

            Parameters
            ----------


            Returns
            -------
            U, V the embedding matrices
        """
        self.u = np.random.rand(self.x.shape[0], self.n_latent_factors)
        self.v = np.random.rand(self.x.shape[1], self.n_latent_factors)

        for _ in range(self.n_iteration):
            self.u = self.generate_embedding_matrix(self.train_set, self.v, self.weight, self.bias_rows,
                                                    self.bias_columns)
            self.v = self.generate_embedding_matrix(self.train_set.T, self.u, self.weight.T, self.bias_columns.T,
                                                    self.bias_rows.T)
            predict_x = self.predict()

            if self.custom_score_function is None:
                self.train_mse_record.append(self.score(self.train_set, predict_x))
                self.test_mse_record.append(self.score(self.test_set, predict_x))
            else:
                self.test_mse_record.append(self.custom_score_function(self.test_set, self.u, self.v,
                                                                       self.regularization, self.weight,
                                                                       self.bias_rows_columns, self.bias_rows,
                                                                       self.bias_columns))

        return self.u, self.v

    def generate_embedding_matrix(self, x: np.ndarray, fixed: np.ndarray, weight: np.ndarray,
                                  bias: np.ndarray, bias_fixed: np.ndarray):
        """
            This method compute the probe.

            - @ : pairwise product (element by element) between matrices
            - * : matrix multiplication (row by column), or pairwise product between a scalar and a matrix

            Parameters
            ----------
            x : dataset

            fixed : embedding matrix used to re-compute the other embedding matrix

            weight : matrix weight of the dataset

            bias : the bias associated with the target embedding matrix

            bias_fixed : the bias associated with the fixed matrix

            Returns
            -------
            Re-computed embedding matrix
        """
        # apply a product among elements on the same column, do it for each column in matrix weight
        transformed_weight = np.reshape(np.prod(weight, axis=0), (1, weight.shape[1]))  # M^(1, weight.n_column)

        # X - mu - B - B_fixed
        a = x - (self.bias_rows_columns + bias + bias_fixed)

        # W @ (X - mu - B - B_fixed)
        a = np.multiply(weight, a)

        # (Fixed.T @ Tras_W) * Fixed) + reg * I_n_latent_factors
        b = np.linalg.multi_dot([fixed.T * transformed_weight, fixed]) + \
            self.regularization * np.identity(self.n_latent_factors)

        # [(Fixed.T @ Tras_W) * Fixed) + reg * I_n_latent_factors]^(-1)
        b_inv = np.linalg.inv(b)

        # W @ (X - mu - B - B_fixed) * Fixed * [(Fixed.T @ Tras_W) * Fixed + reg * I_n_latent_factors]^(-1)
        return np.linalg.multi_dot([a, fixed, b_inv])

    def predict(self):
        """
               This method compute the predicted matrix

               Parameters
               ----------


               Returns
               -------
               Predicted matrix, similar to the given dataset
           """
        return self.u.dot(self.v.T)

    def score(self, actual: np.ndarray, predict: np.ndarray):
        """
               This method compute the score as MSE with the actual dataset
               and the predicted dataset

               Parameters
               ----------
               actual : data_matrix (train or test set)

               predict : approximation of data_matrix

               Returns
               -------
               score, that is mean squared error
        """
        if self.matrix_mask is not None:
            mask = np.zeros(actual.shape, dtype='int')
            for row in range(self.matrix_mask.shape[0]):
                for col in self.matrix_mask[row, :]:
                    mask[row, col] = 1

            mask = np.nonzero(mask)
        else:
            mask = np.nonzero(actual)
        return mean_squared_error(actual[mask], predict[mask])

    def plot(self):
        """
               Plot train and test MSE over the number of iteration.

               Parameters
               ----------


               Returns
               -------
               Nothing
           """
        if self.custom_score_function is None:
            plt.plot(self.train_mse_record, label='Train', linewidth=2)
            plt.ylabel('MSE')
            plt.suptitle('WALS - Mean Square Error')
        else:
            plt.ylabel('Score')
            plt.suptitle('WALS - Custom Score')

        plt.plot(self.test_mse_record, label='Test', linewidth=2)
        plt.xlabel('n° iterations')

        plt.title('n_latent_factors = {0:.2f}, regularization = {1:.2f}, n_iteration = {2}'.
                  format(self.n_latent_factors, self.regularization, self.n_iteration))
        plt.legend(loc='best')
        plt.show()
