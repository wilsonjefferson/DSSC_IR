from exceptions.IRException import IRException


class ColumnValueException(IRException):
    """
        General Exception for the value of a column.

        Parameters
        ----------
        message : exception message
    """
    def __init__(self, message: str):
        super().__init__(message)


class ColumnValueNotExistException(ColumnValueException):
    """
        Exception in case of a value of a column does not exist.

        Parameters
        ----------
        table_name : name of a table

        column_name : name of a column of the table

        column_value : value of the column
    """
    def __init__(self, table_name: str, column_name: str, column_value):
        self.message = "ERROR: in {}, column {}: {} does not exist!".format(table_name, column_name, column_value)
        super().__init__(self.message)
