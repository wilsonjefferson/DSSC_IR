from core.UserCommandLineInterface import UserCommandLineInterface

if __name__ == '__main__':

    songs_csv_file = r'./sources/processed_data/spotify_music/SpotifyFeatures.csv'
    users_csv_file = r'./sources/User.csv'
    history_csv_file = r'./sources/History.csv'
    ratings_csv_file = r'./sources/processed_data/yahoo_music/Ratings.csv'

    cli = UserCommandLineInterface(songs_csv_file, users_csv_file, history_csv_file, ratings_csv_file)
    page_state = cli.login_page()

    while page_state is True:
        page_state = cli.home_page()
