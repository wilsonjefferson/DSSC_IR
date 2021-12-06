from exceptions.sql_handler.sql_handler_exceptions.SQLException import SQLException


class TableException(SQLException):
    """
        General Exception for the tables in the database.

        Parameters
        ----------
        message : exception message
    """
    def __init__(self, message: str):
        super().__init__(message)


class TableNotExistException(TableException):
    """
        Exception in case a certain table does not exist.

        Parameters
        ----------
        table_name : name of a table
    """
    def __init__(self, table_name: str):
        self.message = "ATTENTION: table {} does not exist!".format(table_name)
        super().__init__(self.message)


class TableAlreadyExistException(TableException):
    """
        Exception in case a table already exist.

        Parameters
        ----------
        table_name : name of a table
    """
    def __init__(self, table_name: str):
        self.message = "ATTENTION: table {} already exist!".format(table_name)
        super().__init__(self.message)
