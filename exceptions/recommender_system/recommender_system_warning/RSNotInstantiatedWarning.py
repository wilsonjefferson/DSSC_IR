from exceptions.recommender_system.recommender_system_warning.RSWarning import RSWarning


class RSNotInstantiatedWarning(RSWarning):
    """
        Warning in case a certain set of recommended songs are not available
        because the related Recommender is not instantiated.

        Parameters
        ----------
        recommended_songs : type of recommended songs

        recommender_name : recommender type

        ignore : True if the warning is to be silenced
    """

    def __init__(self, recommended_songs_type, recommender_name: str, ignore: bool = True):
        self.message = "{} recommendation songs are not available: {} is not instantiated.".\
            format(recommended_songs_type, recommender_name)
        if not ignore:
            super().__init__(self.message)
