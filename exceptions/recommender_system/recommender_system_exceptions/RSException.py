from exceptions.IRException import IRException


class RSException(IRException):
    """
        General Exception for the Recommender System.

        Parameters
        ----------
        message : exception message
    """
    def __init__(self, message: str):
        super().__init__(message)
