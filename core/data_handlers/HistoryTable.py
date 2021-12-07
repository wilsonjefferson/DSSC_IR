import random
from core.data_handlers.Table import Table
from datetime import date

from exceptions.ColumnValueWarning import ColumnValueNotExistWarning
from exceptions.IRWarning import IRWarning


class HistoryTable(Table):
    """
        Implement the Table class, this class is to handle the
        history information that is the musical chronology of the users.

        If a path is not given, it means that does not exist a static
        representation of the History Table so, in case user_id and
        song_id are given, a new History Table is created with a first row.
        In case, an sql-ddl query is given, it replace the default sql-ddl
        query to create the History Table.

        Parameters
        ----------
        user_id : ID of the first user inserted in the History Table

        song_id : ID of the first song, listened by the first user,
        inserted in the History Table

        sql : customized sql-ddl query to create the History Table

        path_file : path where find a static representation of the History Table
    """

    def __init__(self, user_id: str = None, song_id: str = None, path_file: str = None, sql: str = None):
        super().__init__('HISTORY')

        if sql is None:
            sql = """CREATE TABLE IF NOT EXISTS """ + self.table_name + """(
                    user_id    text,
                    song_id    text,
                    last_date  date,
                    repetition integer,
                    CONSTRAINT HISTORY_pk PRIMARY KEY (user_id, song_id),
                    CONSTRAINT fk__HISTORY__USERS_c1 
                        FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                    CONSTRAINT fk__HISTORY__USERS_c2
                        FOREIGN KEY (song_id) REFERENCES SONGS(song_id) ON DELETE CASCADE ON UPDATE CASCADE
                );"""

        if path_file:
            if user_id is not None or song_id is not None:
                IRWarning('path file {} is given, other inputs are ignored...'.format(path_file))

            self.sql_handler.load(table_name=self.table_name, sql=sql, path_file=path_file, separator=',')
        else:
            self.sql_handler.create(sql=sql)

            if user_id and song_id:
                if self.user_and_song_exist(user_id, song_id):
                    self.sql_handler.insert(table_name=self.table_name, data=(user_id, song_id, date.today(), 1))

    def add(self, user_id: str, song_id: str):
        """
            Add a new listened song to a certain user in the History table.

            Parameters
            ----------
            user_id : ID of a certain user present in the User table

            song_id : Id of a certain song present in the SOng table

            Returns
            -------
            song_repetition : number of listened repetition
        """
        if self.user_and_song_exist(user_id, song_id):
            if not self.song_not_listened_by_user(user_id, song_id, True):
                IRWarning('song {} has already been listened by user {}, '
                          'increase repetition...'.format(song_id, user_id))
                song_repetition = self.update(user_id, song_id)
            else:
                self.sql_handler.insert(table_name=self.table_name, data=(user_id, song_id, date.today(), 1))
                song_repetition = 1

            return song_repetition

    def create_id(self, args):
        # this class does not need to create any id...
        pass

    def update(self, user_id: str, song_id: str):
        """
            Update number of repetition of a certain song. listened by a certain user. If the song is not
            present in the History of the user, then add it as new listened song.

            Parameters
            ----------
            user_id : ID of a certain user present in the User table

            song_id : ID of a certain song present in the Song table

            Returns
            -------
            song_repetition : number of times the user listened the song
        """
        if not self.item_not_exist(self.table_name, 'user_id', user_id) and not self.song_not_listened_by_user(
                user_id, song_id):
            song_repetition = self.search(conditions=(('repetition',), [('user_id', '=', user_id), 'AND', ('song_id', '=', song_id)])) + 1
            self.sql_handler.update(table_name=self.table_name, conditions=(
                ('repetition', song_repetition), [('user_id', '=', user_id), 'AND', ('song_id', '=', song_id)]))
        elif self.song_not_listened_by_user(user_id, song_id):
            IRWarning('user {} never heard song {} before, added it as new song...'
                      .format(user_id, song_id))
            self.add(user_id, song_id)
        else:
            ColumnValueNotExistWarning(self.table_name, 'user_id', user_id, False)

    def remove(self, item_id: str):
        # this class cannot remove anything:
        # - users are removed from the Users class
        # - songs are removed from the Songs class
        # any removal will be reflected on this class...
        pass

    def drop(self):
        """
            Drop the History table from the database.

            Parameters
            ----------

            Returns
            -------
            Nothing
        """
        self.sql_handler.drop(table_name=self.table_name)

    def store_csv(self, path_file: str = r'../../sources/History.csv', separator: str = '\t'):
        """
            Store the History table in csv file format.

            Parameters
            ----------
            path_file : path where save the csv file

            separator : type of separator for the csv file

            Returns
            -------
            Nothing
        """
        self.sql_handler.store(table_name=self.table_name, path_file=path_file, separator=separator)

    def song_not_listened_by_user(self, user_id: str, song_id: str, ignore: bool = False):
        """
            Method to check if a certain song was listened by a certain user.

            Parameters
            ----------
            user_id : ID of a certain user present in the User table

            song_id : ID of a certain song present in the Song table

            ignore : if the warning has to be ignored

            Returns
            -------
            song_id : ID of the song, if this is not None means that the song
            was already listened by the user
        """
        return song_id not in self.search(
            conditions=(('song_id',), [('user_id', '=', user_id), 'AND', ('song_id', '=', song_id)]), ignore=ignore)

    def add_new_user_with_song(self, user_id: str, song_id: str):
        """
            Method to add a new user directly with an associated song.

            Parameters
            ----------
            user_id : ID of a certain user present in the User table

            song_id : Id of a certain song present in the Song table

            Returns
            -------
            Nothing
        """
        if self.user_and_song_exist(user_id, song_id):
            if self.item_not_exist(self.table_name, 'user_id', user_id):
                self.sql_handler.insert(table_name=self.table_name, data=(user_id, song_id, date.today(), 1))
            else:
                IRWarning('user {} already exist, add {} as new song...'
                          .format(user_id, song_id))
                self.add(user_id, song_id)

    def user_and_song_exist(self, user_id: str, song_id: str):
        """
            Method to check if a certain user AND a certain song are present together in the History table.

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

    def __str__(self):
        return self.sql_handler.print(table_name=self.table_name, column_name='user_id')

    def generator(self, occurrences: int = 100):
        for i in range(1, occurrences):
            user_id = random.choice(self.search(sql='SELECT user_id FROM USERS'))
            song_id = random.choice(self.search(sql='SELECT song_id FROM SONGS'))
            self.add_new_user_with_song(user_id, song_id)


if __name__ == '__main__':
    # history = HistoryTable()
    history = HistoryTable('0', '0')
    # history.add_new_user_with_song('1', '1')
    # history.add_new_user_with_song('0', '0')
    print(history.add('0', '1'))
    history.update('0', '0')
    # print('last date: ' + history.get_column_value('0', '0', 'last_date'))
    print(history)
    # history.store_csv()

    # history.generator(10000)
    # history.store_csv()
