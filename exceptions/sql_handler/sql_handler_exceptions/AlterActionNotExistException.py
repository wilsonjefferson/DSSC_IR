from exceptions.sql_handler.sql_handler_exceptions.SQLException import SQLException


class AlterActionNotExistException(SQLException):
    """
        Exception in case a wrong alter command is given.

        Parameters
        ----------
        action : alter operation
    """
    def __init__(self, action: str):
        self.message = "ATTENTION: action {} does not exist!".format(action)
        super().__init__(self.message)
