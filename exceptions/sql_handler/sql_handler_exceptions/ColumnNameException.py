from exceptions.sql_handler.sql_handler_exceptions.SQLException import SQLException


class ColumnNameException(SQLException):
    """
        General Exception for the name of a column.

        Parameters
        ----------
        message : exception message
    """
    def __init__(self, message: str):
        super().__init__(message)


class ColumnNameNotExistException(ColumnNameException):
    """
        Exception in case a named column does not exist.

        Parameters
        ----------
        table_name : name of a table

        column_name : name of a column
    """
    def __init__(self, table_name: str, column_name: str):
        self.message = "ERROR: in {}, column {} does not exist!".format(table_name, column_name)
        super().__init__(self.message)


class ColumnNameAlreadyExistException(ColumnNameException):
    """
        Exception in case a certain column is already present in a table.

        Parameters
        ----------
        table_name : name of a table

        column_name : name of a column
    """
    def __init__(self, table_name: str, column_name: str):
        self.message = "ERROR: in {}, column {} already exist!".format(table_name, column_name)
        super().__init__(self.message)


class ColumnNameTypeNotNumber(ColumnNameException):
    """
        Exception in case the type of a column is not a number.

        Parameters
        ----------
        table_name : name of a table

        column_name : name of a column
    """
    def __init__(self, table_name: str, column_name: str):
        self.message = "ERROR: in {}, column {} type is not a number!".format(table_name, column_name)
        super().__init__(self.message)
