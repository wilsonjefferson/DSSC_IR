import os.path
from abc import ABC, abstractmethod
from core.data_handlers.SQLHandler import SQLHandler
from exceptions.ColumnValueWarning import ColumnValueNotExistWarning


class Table(ABC):
    """
        Abstract class defining the general structure of a Table.
        This class allows to handle data in the database through
        the SQLHandler class.

        Parameters
        ----------
        table_name : name of the table assign to an instance of this class.
    """

    def __init__(self, table_name: str):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, '../../sources/SQLite_quasi_real_database.db')
        self.table_name = table_name
        self.sql_handler = SQLHandler(db_path)

    @abstractmethod
    def add(self, **kwargs):
        """
            Add new item in the table.

            Parameters
            ----------
            kwargs : inputs variables

            Returns
            -------
            See the implemented method
        """
        raise NotImplementedError

    @abstractmethod
    def create_id(self, args):
        """
            Support method to create unique ID for items.

            Parameters
            ----------
            args : inputs variable

            Returns
            -------
            See the implemented method
        """
        raise NotImplementedError

    def search(self, conditions: tuple = None, sql: str = None, data: tuple = None, flat: bool = True, ignore: bool = False):
        """
            Search data in the table.

            Parameters
            ----------
            conditions : set of conditions for the sql query

            sql : sql query

            data : data for the sql query

            flat : Flat the result if True, otherwise don't flat it

            ignore : if the warning has to be ignored

            Returns
            -------
            rows : resulting set of the research
        """
        rows = self.sql_handler.search(self.table_name, conditions, sql, data, flat)

        if type(rows) is list and len(rows) == 0 and conditions:
            for condition in conditions[1]:
                if type(condition) == tuple:
                    conditional_column = condition[0]
                    conditional_value = condition[2]
                    ColumnValueNotExistWarning(self.table_name, conditional_column, conditional_value, ignore)
            return rows
        else:
            return rows

    @abstractmethod
    def update(self, **kwargs):
        """
            Update rows of a table.

            Parameters
            ----------
            kwargs : inputs variable

            Returns
            -------
            See the implemented method
        """
        raise NotImplementedError

    @abstractmethod
    def remove(self, **kwargs):
        """
            Remove item from the table

            Parameters
            ----------
            kwargs : inputs variable

            Returns
            -------
            See the implemented method
        """
        raise NotImplementedError

    @abstractmethod
    def drop(self):
        """
            Drop the table

            Parameters
            ----------

            Returns
            -------
            Nothing
        """
        raise NotImplementedError

    def item_not_exist(self, table_name, item_name, item_id):
        """
            Method to check if a certain item is present in the table.

            Parameters
            ----------
            table_name : name of the table

            item_name : name of the item

            item_id : ID of the item

            Returns
            -------
            bool : True if item not exist, False otherwise
        """
        rows = self.sql_handler.search(sql='SELECT ' + item_name + ' FROM ' + table_name +
                                           ' WHERE ' + item_name + ' = ?', data=(item_id,))
        if isinstance(rows, list) and len(rows) != 0:
            rows = rows[0]
        return item_id not in rows

    @abstractmethod
    def store_csv(self, path_file: str):
        """
            Store the table in csv file.

            Parameters
            ----------
            path_file : path where save the csv file

            Returns
            -------
            See the implemented method
        """
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def generator(self, occurrences: int = 100):
        raise NotImplementedError
