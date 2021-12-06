from exceptions.IRWarning import IRWarning


class SQLWarning(IRWarning):
    """
        General Exception for the SQL operations.

        Parameters
        ----------
        message : exception message
    """
    def __init__(self, message: str):
        super().__init__(message)
