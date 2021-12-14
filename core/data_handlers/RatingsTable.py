from core.data_handlers.Table import Table
from exceptions.ColumnValueWarning import ColumnValueNotExistWarning, ColumnValueAlreadyExistWarning
from exceptions.input_validation.input_validation_warning.InputValidationWarning import InputOutRangeWarning


class RatingsTable(Table):
    """
        Implement the Table class, this class is to handle the
        preferences of the users on the songs

        It is possible to create the Ratings Table (if not present in
        the database). However, if a path is given, it means a static
        csv file of the Ratings Table exist somewhere and it will be
        loaded in the database instead of create a new one.

        Parameters
        ----------
        sql : customized sql-ddl query to create the Ratings Table

        path_file : path where find a static representation of the
        Ratings Table

        lower_bound : lowest possible rating value

        upper_bound : highest possible rating value
    """

    def __init__(self, sql: str = None, path_file: str = None, lower_bound: int = 1, upper_bound: int = 5):
        super().__init__('RATINGS')
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        if sql is None:
            sql = """CREATE TABLE IF NOT EXISTS RATINGS (
                        user_id text,
                        song_id text,
                        ratings integer,
                        CONSTRAINT RATINGS_pk PRIMARY KEY (user_id, song_id),
                        CONSTRAINT fk__RATINGS__USERS_c1
                            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        CONSTRAINT fk__RATINGS__SONGS_c2
                            FOREIGN KEY (song_id) REFERENCES SONGS(song_id) ON DELETE CASCADE ON UPDATE CASCADE
                    );"""

        if path_file:
            self.sql_handler.load(table_name=self.table_name, sql=sql, path_file=path_file, separator=',')
        else:
            self.sql_handler.create(sql)

    def add(self, user_id: str, song_id: str, rating: int, ignore: bool = True):
        """
            Add a new rating for a certain song by a certain user.

            Parameters
            ----------
            user_id : ID of a certain user

            song_id : ID of a certain song

            rating : rank of the song

            ignore : warning is not displayed if True, otherwise it is

            Returns
            -------
            current_rating : rank of the song
        """
        if self.user_and_song_exist(user_id, song_id):
            if rating >= self.lower_bound or rating <= self.upper_bound:
                if self.rating_already_exist(user_id, song_id, ignore):
                    current_rating = self.search((('ratings',), [('user_id', '=', user_id), 'AND',
                                                                 ('song_id', '=', song_id)]))
                    ColumnValueAlreadyExistWarning(self.table_name, 'ratings', current_rating)
                    self.update(user_id, song_id, rating)
                else:
                    self.sql_handler.insert(table_name=self.table_name, data=(user_id, song_id, rating))
                return self.search((('ratings', ), [('user_id', '=', user_id), 'AND', ('song_id', '=', song_id)]))
            else:
                InputOutRangeWarning(self.table_name, 'ratings', rating, [self.lower_bound, self.upper_bound], False)

    def user_and_song_exist(self, user_id: str, song_id: str):
        """
            Method to check if a certain user AND a certain song are present together in the Ratings table.

            Parameters
            ----------
            user_id : ID of a user

            song_id : ID of a song

            Returns
            -------
            bool : True if the pair (user, song) exist, False otherwise
        """
        if self.item_not_exist('USERS', 'user_id', user_id):
            ColumnValueNotExistWarning('USERS', 'user_id', user_id)
        elif self.item_not_exist('SONGS', 'song_id', song_id):
            ColumnValueNotExistWarning('SONGS', 'song_id', song_id)
        else:
            return True
        return False

    def rating_already_exist(self, user_id: str, song_id: str, ignore: bool):
        """
            Method to check if a certain song has a rating by a certain user

            Parameters
            ----------
            user_id : ID of a user

            song_id : ID of a song

            Returns
            -------
            bool : True if the pair (user, song) exist, False otherwise
        """
        rating = self.search((('ratings',), [('user_id', '=', user_id), 'AND', ('song_id', '=', song_id)]), ignore=ignore)

        if type(rating) == list:
            if len(rating) != 0:
                return True
        elif rating != 0:
            return True

        return False

    def create_id(self, args):
        # this class does not need to create any id...
        pass

    def update(self, user_id: str, song_id: str, new_rating: int):
        """
            Update information about a given user AND song.

            Parameters
            ----------
            user_id : ID of a certain user

            song_id : ID of a certain song

            new_rating : the value to upload in the Ratings table

            Returns
            -------
            Nothing
        """
        if self.user_and_song_exist(user_id, song_id):

            current_rating = self.search((('ratings',), [('user_id', '=', user_id), 'AND',  ('song_id', '=', song_id)]))
            if current_rating != 0:
                self.sql_handler.update(self.table_name, (('ratings', new_rating), [('user_id', '=', user_id), 'AND',
                                                                                    ('song_id', '=', song_id)]))
                print(self)
            else:
                ColumnValueNotExistWarning(self.table_name, 'ratings', current_rating)
                self.add(user_id, song_id, new_rating)

    def remove(self, user_id: str, song_id: str):
        """
            Method to remove an existing rating from the Ratings table.

            Parameters
            ----------
            user_id : ID of a certain user

            song_id : ID of a certain song

            Returns
            -------
            Nothing
        """
        if self.user_and_song_exist(user_id, song_id):
            self.sql_handler.delete(self.table_name, ((), [('user_id', '=', user_id), 'AND',
                                                           ('song_id', '=', song_id)]))

    def drop(self):
        """
            Drop the Ratings table from the database.

            Parameters
            ----------


            Returns
            -------
            Nothing
        """
        self.sql_handler.drop(table_name=self.table_name)

    def store_csv(self, path_file: str = r'../../sources/Ratings.csv'):
        """
            Method to store the Ratings table in csv file

            Parameters
            ----------
            path_file : path where save the csv file

            Returns
            -------
            Nothing
        """
        self.sql_handler.store(self.table_name, path_file)

    def __str__(self):
        return self.sql_handler.print(table_name=self.table_name, column_name='user_id')

    def generator(self, occurrences: int = 100):
        pass
