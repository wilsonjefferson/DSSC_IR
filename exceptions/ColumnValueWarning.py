import warnings
from exceptions.IRWarning import IRWarning


class ColumnValueWarning(IRWarning):
    """
        General Warning for column value.

        Parameters
        ----------
        message : warning message
    """
    def __init__(self, message: str):
        super().__init__(message)


class ColumnValueNotExistWarning(ColumnValueWarning):
    """
        Warning in case a value of a certain column does not exist.

        Parameters
        ----------
        table_name : name of a table

        column_name : name of a column

        column_value : value of a column

        ignore : True if the warning is to be silenced
    """
    def __init__(self, table_name: str, column_name: str, column_value, ignore: bool = True):
        self.message = "in {}, column {}: {} does not exist!".format(table_name, column_name, column_value)
        if not ignore:
            super().__init__(self.message)


class ColumnValueAlreadyExistWarning(ColumnValueWarning):
    """
        Warning in case a value of a certain column already exist.

        Parameters
        ----------
        table_name : name of a table

        column_name : name of a column

        column_value : value of a column

        ignore : True if the warning is to be silenced
    """
    def __init__(self, table_name: str, column_name: str, column_value, ignore: bool = True):
        self.message = "in {}, column {}: {} already exist!".format(table_name, column_name, column_value)
        if not ignore:
            super().__init__(self.message)
