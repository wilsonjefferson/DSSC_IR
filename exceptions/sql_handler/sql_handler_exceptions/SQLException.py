from exceptions.IRException import IRException


class SQLException(IRException):
    """
        General Exception for the SQL operations.

        Parameters
        ----------
        message : exception message
    """
    def __init__(self, message: str):
        super().__init__(message)
