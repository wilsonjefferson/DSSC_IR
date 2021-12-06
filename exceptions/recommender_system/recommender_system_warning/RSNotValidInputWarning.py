from exceptions.recommender_system.recommender_system_warning.RSWarning import RSWarning


class RSNotValidInputWarning(RSWarning):
    """
        Warning in case a certain input is not valid for a function of the
        specific recommender system.

        Parameters
        ----------
        recommender_name : recommender type

        input_variable : invalid input variable

        ignore : True if the warning is to be silenced
    """

    def __init__(self, input_variable, recommender_name: str, ignore: bool = True):
        self.message = "{} recommender: {} is not a valid input.".\
            format(recommender_name, input_variable)
        if not ignore:
            super().__init__(self.message)
