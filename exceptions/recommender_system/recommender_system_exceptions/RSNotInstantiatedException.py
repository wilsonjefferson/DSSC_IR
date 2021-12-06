from exceptions.recommender_system.recommender_system_exceptions.RSException import RSException


class RSNotInstantiatedException(RSException):
    """
        Exception in case a Recommender System is not instantiated.

        Parameters
        ----------

    """
    def __init__(self):
        self.message = "ERROR: Recommender Systems are not instantiated!"
        super().__init__(self.message)
