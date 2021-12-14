from core.data_handlers.RatingsTable import RatingsTable
from core.recommender_systems.MusicRSHandler import MusicRSHandler
from core.data_handlers.SongTable import SongTable
from core.data_handlers.HistoryTable import HistoryTable
from core.data_handlers.UserTable import UserTable


class UserCommandLineInterface:
    """
        This class represent the interface between the user and the
        entire system, it is the only point of contact and for that
        reason it is a critical point of the system. Through this
        class, the user is able to login, navigate in the system and
        listen a lot of music.

        P.s. csv files may be required in case the DB is not available
        or in case it is empty.

        Parameters
        ----------
        users_csv_file : path where find the csv of the users

        songs_csv_file : path where find the csv of the songs

        history_csv_file : path where find the csv of the histories

        ratings_csv_file : path where find the csv of the ratings
    """

    def __init__(self, songs_csv_file: str = None, users_csv_file: str = None,
                 history_csv_file: str = None, ratings_csv_file: str = None):
        self.songs = SongTable(path_file=songs_csv_file)
        self.users = UserTable(path_file=users_csv_file)
        self.history = HistoryTable(path_file=history_csv_file)
        self.ratings = RatingsTable(path_file=ratings_csv_file)
        self.music_recommender = MusicRSHandler()
        self.current_user_id = None
        self.current_song_id = None

    def login_page(self):
        """
            This function will prompt the login page to the user.

            Parameters
            ----------


            Returns
            -------
            bool : True in case state is remain the same
        """

        print('Welcome to Spotify!')
        username = input('username: ')
        password = input('password: ')
        user_id = self.users.search(conditions=(('user_id', ),
                                                [('username', '=', username), 'AND', ('password', '=', password)]))
        if not user_id:
            print('CONSOLE')
            print('- Press 0 to refresh the page')
            print('- Press 1 to create a new account')
            print('- Press anything else to quit')
            user_opt = input('user option: ')
            if user_opt == '0':
                print('REFRESH PAGE...')
                self.login_page()
            elif user_opt == '1':
                print('CREATING A NEW ACCOUNT...')
                username = input('username: ')
                password = input('password: ')
                email = input('email: ')
                nationality = input('nationality: ')
                self.current_user_id = self.users.add(username, password, email, nationality)
            else:
                print('QUITTING PAGE...')
                exit(0)
        else:
            self.current_user_id = user_id
        return True

    def home_page(self):
        """
            This print the recommendations from each Recommender System.

            Parameters
            ----------


            Returns
            -------
            bool : False in case change state to termination
        """

        print('\nUSER:{0} - DASHBOARD'.format(self.current_user_id))
        print('|| RECOMMENDED SONGS ||\n')
        self.music_recommender.refresh()
        recommendation = self.music_recommender.recommend_songs(current_user_id=self.current_user_id,
                                                                current_song_id=self.current_song_id,
                                                                column_names=['popularity'])

        for position, item in enumerate(recommendation.items()):
            song_description = self.songs.search(conditions=(('song_name', 'artist_name'), [('song_id', '=', item[0])]))
            if song_description:
                print('{0}: {1} - {2}, {3}'.format(position, item[0], song_description[0], song_description[1]))
        print()

        self.music_recommender.print_recommenders_songs()  # print recommendations from each RS

        print('CONSOLE')
        print('- Press 0 to play a song')
        print('- Press 1 to logout')
        print('- Press 2 to rate a song')
        print('- Press anything to quit\n')

        user_opt = input('user option: ')
        if user_opt == '0':
            print('PLAY A SONG...')
            song_id = input('play (song id): ')
            song_description = self.songs.search(conditions=(('*',), [('song_id', '=', song_id)]), flat=True)
            if song_description:
                self.current_song_id = song_description[0]
                song_name = song_description[3]
                genre = song_description[1]
                artist_name = song_description[2]
                print('{0} from {1} - genre: {2}, song_id: {3}'.format(song_name, artist_name, genre, self.current_song_id))
                print('PLAYING SONG...')
                self.history.add(self.current_user_id, self.current_song_id)
                self.music_recommender.listened_song_by_user(self.current_song_id)
            return self.home_page()
        elif user_opt == '1':
            print('LOGOUT...')
            return self.login_page()
        elif user_opt == '2':
            print('RATING...')
            song_id = input('song id: ')
            song_description = self.songs.search(conditions=(('*',), [('song_id', '=', song_id)]))
            if song_description:
                print('RANGE OF RATING: [1, 2, 3, 4, 5]')
                rating_song = int(input('rating for {0}: '.format(song_id)))
                self.ratings.add(self.current_user_id, song_id, rating_song)
                return self.home_page()
        else:
            print('QUITTING...')
            return False
