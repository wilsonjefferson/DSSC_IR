from core.recommender_systems.CoolStartRS import CoolStartRS
from core.recommender_systems.RSWeighter import RSWeighter
from core.recommender_systems.RecommenderSystem import RecommenderSystem
from core.recommender_systems.RelevanceBasedRS import RelevanceBasedRS
from core.recommender_systems.UserBasedRS import UserBasedRS
from core.recommender_systems.WeightedMFBasedRS import WeightedMFBasedRS
from exceptions.recommender_system.recommender_system_warning.RSNotInstantiatedWarning import RSNotInstantiatedWarning


class MusicRSHandler(RecommenderSystem):
    """
        This class handle all the recommenders systems used to provide
        items to the user, according his/her interests and the interest
        of all the other users.

        According a defined weight-assessment only N songs are suggested
        to the user in respect the overall suggested songs, these N are
        the most likely songs that the user might be like.

        Parameters
        ----------

    """

    def __init__(self):
        super().__init__()
        self.rec_songs = {}
        self.recommenders = None
        self.recommendations = None
        self.rs_weighter = None

    def refresh(self):
        """
            This method allows to refresh the knowledge of the recommenders systems.
            If a refresh is applied, then all the RS are resetted and they will re-apply
            all their internal procedure to define a new set of suggested items.

            This method is called by default when a new instance of this class is created.

            Parameters
            ----------

            Returns
            -------
            Nothing
        """

        self.recommenders = {}  # {recommender_name: recommender, ..., recommender_name: recommender}
        self.recommendations = {}  # {recommender_name: recommended_songs, ..., recommender_name: recommended_songs}

        if self.exist('SONGS') and self.exist('HISTORY'):
            self.recommenders['CoolStartRS'] = CoolStartRS()

        if self.exist('SONGS'):
            self.recommenders['RelevanceBasedRS'] = RelevanceBasedRS('SONGS')

        if self.exist('RATINGS') and self.exist('RATINGS'):
            self.recommenders['WeightedMFBasedRS'] = WeightedMFBasedRS(regularization=0.05, n_latent_factors=20, n_iteration=111)

        if self.exist('SONGS') and self.exist('HISTORY'):
            self.recommenders['UserBasedRS'] = UserBasedRS()

        self.rs_weighter = RSWeighter()

    def exist(self, table_name: str):
        return self.sql_handler.exist(table_name) and not self.sql_handler.is_empty(table_name)

    def execute_recommender(self, recommender_name: str, rs_suggestions: dict, n_recommenders: int, *args):
        """
            Support method to execute the recommendation search by a certain
            Recommender System.

            Parameters
            ----------
            recommender_name : name of the Recommender System

            rs_suggestions : collection of results from each Recommender System

            n_recommenders : counter of Recommender System activated according
            existing tables in DB

            args : dictionary of inputs for the Recommender System

            Returns
            -------
            rs_suggestions : updated collection with results from the Recommender System

            n_recommenders : updated counter of activated Recommender System
        """
        self.recommendations[recommender_name] = self.recommenders[recommender_name].recommend_songs(*args)
        rs_suggestions[self.recommenders[recommender_name]] = self.recommendations[recommender_name]
        n_recommenders += 1

        return rs_suggestions, n_recommenders

    def recommend_songs(self, current_user_id: str = None, current_song_id: str = None, column_names: list = None,
                        n_songs: int = 10):
        """
            This method provide N suggested items to the user as a "combination" of
            the recommenders system's suggestions. At each RS is associated a weight
            given by a certain rules. Then, a score for each songs is computed as a
            weighted average of RS weight and song repetition.

            The N songs with higher score are suggested to the user.

            Parameters
            ----------
            current_user_id : ID of the current logged user

            current_song_id : ID of the last song listened by the current user

            column_names : set of column for the RelevanceRS

            n_songs : number of songs to suggest to the user

            Returns
            -------
            rec_songs : set of N recommended songs
        """

        n_recommenders = 0
        rs_suggestions = {}  # {recommender: recommended_songs, ..., recommender: recommended_songs}

        if 'CoolStartRS' in self.recommenders and current_user_id is not None and current_song_id is not None:
            rs_suggestions, n_recommenders = self.execute_recommender('CoolStartRS', rs_suggestions, n_recommenders,
                                                                      current_user_id, current_song_id, n_songs)

        if 'RelevanceBasedRS' in self.recommenders and column_names is not None:
            rs_suggestions, n_recommenders = self.execute_recommender('RelevanceBasedRS', rs_suggestions,
                                                                      n_recommenders, column_names, n_songs)

        if 'WeightedMFBasedRS' in self.recommenders:
            rs_suggestions, n_recommenders = self.execute_recommender('WeightedMFBasedRS', rs_suggestions,
                                                                      n_recommenders, current_user_id, n_songs)

        if 'UserBasedRS' in self.recommenders and current_song_id is not None:
            rs_suggestions, n_recommenders = self.execute_recommender('UserBasedRS', rs_suggestions, n_recommenders,
                                                                      current_user_id, current_song_id, n_songs)

        self.rs_weighter.set(rs_suggestions=rs_suggestions)
        rs_weights = self.rs_weighter.uniform_weight()

        # [{song_id: score, ..., song_id: score}, ..., {song_id: score, ..., song_id: score}]
        recommender_songs = list(rs_suggestions.values())  # from recommenders

        # song_id_tot_score = (sum(song_id_score_recommender_i * weight_recommender_i)) / number_recommenders
        for idx in range(n_recommenders):
            for song_id, score in list(recommender_songs[idx].items()):
                if song_id not in self.rec_songs.keys():
                    self.rec_songs[song_id] = score * rs_weights[idx]
                else:
                    self.rec_songs[song_id] = self.rec_songs.get(song_id) + (score * rs_weights[idx])

        for song_id in self.rec_songs.keys():
            self.rec_songs[song_id] = self.rec_songs.get(song_id) / n_recommenders

        # sort according scores in decreasing order and pick first n_songs for the dict
        self.rec_songs = dict(sorted(self.rec_songs.items(), key=lambda item: item[1], reverse=True)[:n_songs])

        return self.rec_songs

    def listened_song_by_user(self, song_id: str):
        """
            This method let the RSWeighter knows which song the user decided
            to listen, so it can update RS weights accordingly.

            Parameters
            ----------
            song_id : ID of the listened song by the user

            Returns
            -------
            Nothing
        """
        self.rs_weighter.set(listened_song_id=song_id)

    def cool_recommended(self):
        """
            This method provide the recommendation of the CoolStartRS.

            Parameters
            ----------

            Returns
            -------
            Set of recommended songs
        """
        if self.recommendations.get('CoolStartRS', None) is None:
            RSNotInstantiatedWarning('cold', 'CoolStartRS', False)
            return {}
        else:
            return self.recommendations['CoolStartRS']

    def relevance_recommended(self):
        """
            This method provide the recommendation of the RelevanceBasedRS.

            Parameters
            ----------

            Returns
            -------
            Set of recommended songs
        """
        if self.recommendations.get('RelevanceBasedRS', None) is None:
            RSNotInstantiatedWarning('relevant', 'RelevanceBasedRS', False)
            return {}
        else:
            return self.recommendations['RelevanceBasedRS']

    def wmf_recommended(self):
        """
            This method provide the recommendation of the WeightedMFBasedRS.

            Parameters
            ----------

            Returns
            -------
            Set of recommended songs
        """
        if self.recommendations.get('WeightedMFBasedRS', None) is None:
            RSNotInstantiatedWarning('collaborative', 'WeightedMFBasedRS', False)
            return {}
        else:
            return self.recommendations['WeightedMFBasedRS']

    def user_based_recommended(self):
        """
            This method provide the recommendation of the WeightedMFBasedRS.

            Parameters
            ----------

            Returns
            -------
            Set of recommended songs
        """
        if self.recommendations.get('UserBasedRS', None) is None:
            RSNotInstantiatedWarning('collaborative', 'UserBasedRS', False)
            return {}
        else:
            return self.recommendations['UserBasedRS']

    def print_recommenders_songs(self):
        """
            This print the recommendations from each Recommender System.

            Parameters
            ----------


            Returns
            -------
            Nothing
        """
        for recommender in list(self.recommenders.values()):
            print(recommender)

    def __str__(self):
        return super().print('MusicRSHandler', self.rec_songs) if self.rec_songs else ''
