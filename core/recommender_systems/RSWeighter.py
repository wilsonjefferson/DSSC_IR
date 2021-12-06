from core.recommender_systems.CoolStartRS import CoolStartRS
from core.recommender_systems.RelevanceBasedRS import RelevanceBasedRS
from exceptions.recommender_system.recommender_system_exceptions.RSNotInstantiatedException import \
    RSNotInstantiatedException
from exceptions.recommender_system.recommender_system_warning.RSWarning import RSWarning


class RSWeighter:
    """
        This class assign weights to recommenders systems according
        different strategies.

        Parameters
        ----------

    """

    def __init__(self):
        self.recommenders = None
        self.listened_song_id = None

    def set(self, rs_suggestions: dict = None, listened_song_id: str = None):
        """
            Setter method. It set the attribute of this class.

            Parameters
            ----------
            rs_suggestions : set of recommenders systems with their suggested items

            listened_song_id : ID of the song listened by the user

            Returns
            -------
            Nothing
        """
        if rs_suggestions is not None and listened_song_id is None:
            self.recommenders = rs_suggestions
        elif rs_suggestions is None and listened_song_id is not None:
            self.listened_song_id = listened_song_id
        else:
            RSWarning('in RSWeigher.set, rs_suggestions and listened_song_id cannot be both None or bot not None.')

    def uniform_weight(self):
        """
            This method provide the a uniform weights to the set
            of recommender systems.

            Parameters
            ----------

            Returns
            -------
            Set of RS's weights
        """
        if self.recommenders is None:
            raise RSNotInstantiatedException()

        return [1.0 / len(self.recommenders) for _ in range(len(self.recommenders))]


if __name__ == '__main__':
    cold_start_recommender = CoolStartRS()
    relevance_recommender = RelevanceBasedRS('SONGS')

    cold_songs = cold_start_recommender.recommend_songs('U-0000', 'S-000')
    relevance_songs = relevance_recommender.recommend_songs(['popularity'])

    rs_weighter = RSWeighter()
    rs_weighter.set({cold_start_recommender: cold_songs, relevance_recommender: relevance_songs})
    rs_weighter.uniform_weight()
