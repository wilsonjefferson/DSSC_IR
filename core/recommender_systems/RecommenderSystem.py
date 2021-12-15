import os
from abc import abstractmethod
from core.data_handlers.SQLHandler import SQLHandler


class RecommenderSystem:
    """
        It is an abstract class representing the general Recommender System.

        Parameters
        ----------
        table_name : name of the table used by an implementation of this class
    """

    def __init__(self, table_name: str = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, '../../sources/SQLite_quasi_real_database.db')
        self.sql_handler = SQLHandler(db_path)
        self.table_name = table_name

    @abstractmethod
    def recommend_songs(self, **kwargs):
        """
            This method have to be implemented according the kind of Recommender System.
            It should provide a certain number of recommended songs to the user.

            Parameters
            ----------
            kwargs : input parameters

            Returns
            -------
            list of recommended songs
        """
        raise NotImplementedError

    def print(self, recommender_name: str, rec_songs: dict):
        """
            This method have is used by the sub-classes to print their
            recommended songs.

            Parameters
            ----------
            recommender_name : name of the recommender

            rec_songs : recommended songs with scores

            Returns
            -------
            message : the printable message of the recommender
        """
        message = recommender_name + '\n'
        for position, item in enumerate(rec_songs.items()):
            message += str(position) + ': ' + item[0] + ' ' + str(item[1]) + '\n'
        message += '\n'
        return message
