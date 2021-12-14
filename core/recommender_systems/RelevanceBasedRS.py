import pandas as pd

from core.recommender_systems.RecommenderSystem import RecommenderSystem
from exceptions.sql_handler.sql_handler_exceptions.ColumnNameException import ColumnNameTypeNotNumber


class RelevanceBasedRS(RecommenderSystem):
    """
        Implement the RecommenderSystem class, this class just need
        a given table name and it will recommend N songs according
        a descending sort of a certain column of the given table.

        WARNING: the table need the song_id column.

        Parameters
        ----------
        table_name : name of the table on which the RelevanceBasedRS will find
        the recommended songs
    """

    def __init__(self, table_name: str):
        super().__init__(table_name)
        self.rec_songs = {}
        self.columns_of_number_type = self.sql_handler.select_columns(table_name=self.table_name,
                                                                      data_types=['integer', 'double'])

    def recommend_songs(self, column_names: list, n_songs: int = 10):
        """
            Recommend n_songs according columns values, in descending order.

            Parameters
            ----------
            column_names : ID of the logged user

            n_songs : number of songs to be recommended

            Returns
            -------
            list of recommended songs by ID
        """
        for column_name in column_names:
            if column_name not in self.columns_of_number_type:
                raise ColumnNameTypeNotNumber(self.table_name, column_name)

        column_order_conditions = ''.join([column_name + ' DESC, ' for column_name in column_names])[:-2]

        rows = self.sql_handler.search(sql='SELECT song_id, ' + column_order_conditions +
                                           ' FROM ' + self.table_name + ' ORDER BY ' + column_order_conditions)

        rows = pd.DataFrame(rows, columns=['song_id'] + column_names)
        rows[column_names] = rows[column_names].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

        list_rows = rows.values

        for row in range(n_songs):
            for idx in range(1, len(list_rows[row])):
                self.rec_songs[list_rows[row][0]] = list_rows[row][idx]

        return self.rec_songs

    def __str__(self):
        return self.print('RelevanceBasedRS', self.rec_songs) if self.rec_songs else ''
