from abc import abstractmethod
import numpy as np


class GeneralModel:
    """
        This is an abstract class in which is given the general structure
        for the WMF algorithm.

        Parameters
        ----------

    """

    def __init__(self):
        self.x = None
        self.train_set = None
        self.test_set = None
        self.matrix_mask = None

    def split(self):
        """
            This method crate the train and test set. In particular, the train set
            is build starting from the dataset, but for each row of the dataset,
            a certain number of no-zero values are masked in the train set. These
            masked values are available in the test set.

            Parameters
            ----------


            Returns
            -------
            arrays_of_random_no_zero_column_index : the matrix taking track of the masked
            values for each row of the dataset
        """
        train_set = self.x.copy()
        test_set = np.zeros(self.x.shape)
        ten_percent_test_size = int(10 * self.x.shape[0] / 100)
        self.matrix_mask = []
        for row in range(self.x.shape[0]):
            no_zero_flatted_row = np.flatnonzero(self.x[row])
            random_no_zero_column_index = np.random.choice(a=no_zero_flatted_row,
                                                           size=ten_percent_test_size if
                                                           len(no_zero_flatted_row) else
                                                           len(no_zero_flatted_row),
                                                           replace=False)
            test_set[row, random_no_zero_column_index] = self.x[row, random_no_zero_column_index]
            train_set[row, random_no_zero_column_index] = 0.0
            self.matrix_mask.append(random_no_zero_column_index)

        self.matrix_mask = np.array([np.array(element, dtype="int") for element in
                                     self.matrix_mask])
        self.train_set = train_set
        self.test_set = test_set
        return self.matrix_mask

    @abstractmethod
    def fit(self, **kwargs):
        """
            This method train the model on the training set.

            Parameters
            ----------
            kwargs : input parameters

            Returns
            -------
            See the implementation of that method
        """
        raise NotImplementedError

    @abstractmethod
    def score(self, **kwargs):
        """
            This method compute the score of the model.

            Parameters
            ----------
            kwargs : input parameters

            Returns
            -------
            See the implementation of that method
        """
        raise NotImplementedError
