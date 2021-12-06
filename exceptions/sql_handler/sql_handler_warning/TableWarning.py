from exceptions.sql_handler.sql_handler_warning.SQLWarning import SQLWarning


class TableWarning(SQLWarning):
    """
        General Warning for the tables in the database.

        Parameters
        ----------
        message : exception message
    """
    def __init__(self, message: str):
        super().__init__(message)


class TableNotExistWarning(TableWarning):
    """
        Warning in case a table not exist

        Parameters
        ----------
        table_name : name of a table

        ignore : True if the warning is to be silenced
    """
    def __init__(self, table_name: str, ignore: bool = True):
        self.message = "no such table: {}".format(table_name)
        if not ignore:
            super().__init__(self.message)


class TableAlreadyExistWarning(TableWarning):
    """
        Warning in case a table not exist

        Parameters
        ----------
        table_name : name of a table

        ignore : True if the warning is to be silenced
    """
    def __init__(self, table_name: str, ignore: bool = True):
        self.message = "table {} already exist.".format(table_name)
        if not ignore:
            super().__init__(self.message)
