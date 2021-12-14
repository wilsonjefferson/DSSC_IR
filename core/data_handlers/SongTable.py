from core.data_handlers.Table import Table
from exceptions.ColumnValueWarning import ColumnValueNotExistWarning, ColumnValueAlreadyExistWarning


class SongTable(Table):
    """
        Implement the Table class, this class is to handle the
        songs information in the database.

        If a Songs Table does not exist in the database, a static representation
        of the Songs Table is loaded in the database by means of csv file,
        passed through a path file.

        Parameters
        ----------
        path_file : path where find a static representation of the Songs Table
    """

    def __init__(self, path_file: str = r'../sources/processed_data/spotify_music/SpotifyFeatures.csv'):
        super().__init__('SONGS')
        sql = """CREATE TABLE IF NOT EXISTS """ + self.table_name + """(
                        song_id text PRIMARY KEY,
                        genre text NOT NULL,
                        artist_name text NOT NULL,
                        song_name text NOT NULL,
                        popularity integer NOT NULL,
                        acousticness double NOT NULL,
                        danceability double NOT NULL,
                        duration_ms integer NOT NULL,
                        energy double NOT NULL,
                        instrumentalness double NOT NULL,
                        key text NOT NULL,
                        liveness double NOT NULL, 
                        loudness double NOT NULL,
                        mode text NOT NULL,
                        speechiness double NOT NULL,
                        tempo double NOT NULL,
                        time_signature text NOT NULL,
                        valence double NOT NULL
                    );
                    """

        self.sql_handler.load(table_name=self.table_name, sql=sql, path_file=path_file, separator=',')

    def add(self, *args):
        """
            Add a new song in the Song table

            Parameters
            ----------
            args : set of inputs variables

            Returns
            -------
            song_id : unique ID of the new song
        """
        sql = 'SELECT song_id FROM ' + self.table_name + ' WHERE genre = ? AND artist_name = ? AND song_name = ? ' \
              'AND popularity = ? AND acousticness = ? AND danceability = ? AND duration_ms = ? ' \
              'AND energy = ? AND instrumentalness = ? AND key = ? AND liveness = ? ' \
              'AND loudness = ? AND mode = ? AND speechiness = ? AND tempo = ? AND time_signature = ? ' \
              'AND valence = ?'

        data = args
        # data = (genre, artist_name, song_name, popularity, acousticness, danceability, duration_ms, energy,
        #        instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence)

        song_id = self.search(sql=sql, data=data)
        if song_id:
            ColumnValueAlreadyExistWarning(self.table_name, 'song_id', song_id)
            return song_id

        last_song_id = self.sql_handler.search(sql='SELECT song_id FROM ' + self.table_name)
        if type(last_song_id) is list and len(last_song_id) >= 1:
            last_song_id.sort(key=lambda x: int(x[0]))
            last_song_id = last_song_id[-1][0]
        song_id = self.create_id(last_song_id)
        data = (song_id,) + data

        self.sql_handler.insert(table_name=self.table_name, data=data)
        return song_id

    def create_id(self, last_id):
        """
            Support method to create a new unique user ID: ID are created with an integer increased number.

            Parameters
            ----------
            last_id : last created user ID

            Returns
            -------
            str : new user ID
        """
        if type(last_id) == list and len(last_id) == 0: # in case of first user (admin)
            return '0'
        else:
            digits = str(int(last_id)+1)
            return digits

    def update(self, song_id: str, column_name: str, new_column_value):
        """
            Update information about an existing song in the Song Table.

            Parameters
            ----------
            song_id : ID of a certain song

            column_name : name of the column in Song table

            new_column_value : new value for the given column

            Returns
            -------
            Nothing
        """
        if self.check_column_value_validity(song_id, column_name):
            self.sql_handler.update(table_name=self.table_name,
                                    conditions=((column_name, new_column_value), [('song_id', '=', song_id)]))

    def remove(self, song_id: str):
        """
            Remove a song by songID

            Parameters
            ----------
            song_id : ID of a certain song

            Returns
            -------
            Nothing
        """
        self.sql_handler.delete(table_name=self.table_name, conditions=((), [('song_id', '=', song_id)]))

    def drop(self):
        """
            Drop Song table.

            Parameters
            ----------


            Returns
            -------
            Nothing
        """
        self.sql_handler.drop(table_name=self.table_name)

    def store_csv(self, path_file: str = '../../sources/Songs.csv'):
        """
            Store the Song table in csv file format.

            Parameters
            ----------
            path_file : path where store the csv file

            Returns
            -------
            Nothing
        """
        self.sql_handler.store(table_name=self.table_name, path_file=path_file, separator=',')

    def check_column_value_validity(self, song_id: str, column_name: str):
        """
            Method to check if a certain column is valid.

            Parameters
            ----------
            song_id : ID of a certain song

            column_name : column name in the Song table

            Returns
            -------
            bool : True if it is valid, False otherwise
        """
        if self.sql_handler.column_not_exist('SONGS', column_name):
            return False
        if self.item_not_exist(self.table_name, 'song_id', song_id):
            ColumnValueNotExistWarning(self.table_name, 'song_id', song_id)
            return False
        return True

    def __str__(self):
        return self.sql_handler.print(table_name=self.table_name, column_name='song_id')

    def generator(self, occurrences: int = 100):
        pass
