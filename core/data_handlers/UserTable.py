import random

from core.data_handlers.Table import Table
from exceptions.ColumnValueWarning import ColumnValueNotExistWarning, ColumnValueAlreadyExistWarning
from exceptions.IRWarning import IRWarning


class UserTable(Table):
    """
        Implement the Table class, this class is to handle the
        users information in the database.

        It is possible to create the User Table (if not present in the
        database) with the information of the first user. However, if
        a path is given, it means a static csv file of the User Table
        exist somewhere and it will be loaded in the database instead
        of create a new one.

        Parameters
        ----------
        username : username of the first user inserted in the User Table

        password : password of the first user inserted in the User Table

        email : email of the first user inserted in teh User Table

        sql : customized sql-ddl query to create the User Table

        path_file : path where find a static representation of the User Table
    """

    def __init__(self, username: str = None, password: str = None, email: str = None, sql: str = None, path_file: str = None):
        super().__init__('USERS')

        if sql is None:
            sql = """CREATE TABLE IF NOT EXISTS USERS (
                                                    user_id text PRIMARY KEY,
                                                    username text UNIQUE,
                                                    password text NOT NULL,
                                                    email text UNIQUE,
                                                    nationality text
                                                );"""

        if path_file:
            if username is not None or password is not None or email is not None:
                IRWarning('path file {} is given, other inputs are ignored...'.format(path_file))

            self.sql_handler.load(table_name=self.table_name, sql=sql, path_file=path_file, separator=',')
        else:
            self.sql_handler.create(sql)

            if '0' not in self.search(conditions=(('user_id', ), [('user_id', '=', '0')]), ignore=True):
                username = 'admin' if username is None else username
                password = 'pwd' if password is None else password
                email = 'admin@gmail.com' if email is None else email
                self.add(username, password, email, None)

    def add(self, username: str, password: str, email: str, nationality: str = None, ignore: bool = True):
        """
            Add a new user in the user table.

            Parameters
            ----------
            username : name of the user

            password : password of the user

            email : email of the user

            nationality : nationality of the user

            ignore : ignore warning if True, otherwise don't ignore it

            Returns
            -------
            user_id : unique user ID
        """
        user_id = None
        for column_name, column_value in [['username', username], ['email', email]]:
            if self.column_value_already_used(column_name, column_value, ignore):
                return user_id
        last_user_id = self.sql_handler.search(sql='SELECT user_id FROM ' + self.table_name)
        if type(last_user_id) is list and len(last_user_id) >= 1:
            last_user_id.sort(key=lambda x: int(x[0]))
            last_user_id = last_user_id[-1][0]
        user_id = self.create_id(last_user_id)
        self.sql_handler.insert(self.table_name, (user_id, username, password, email, nationality))

        return user_id

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

    def update(self, user_id: str, column_name: str, new_column_value):
        """
            Update information about a given user.

            Parameters
            ----------
            user_id : ID of a certain user

            column_name : column of the User table to be update

            new_column_value : the value to upload in the user table

            Returns
            -------
            Nothing
        """
        if self.check_column_value_validity(user_id, column_name):
            self.sql_handler.update(self.table_name, ((column_name, new_column_value), [('user_id', '=', user_id)]))

    def remove(self, user_id: str):
        """
            Method to remove an existing user from the User table.

            Parameters
            ----------
            user_id : ID of a certain user

            Returns
            -------
            Nothing
        """
        if self.item_not_exist('USERS', 'user_id', user_id):
            ColumnValueNotExistWarning('USERS', 'user_id', user_id)
        else:
            self.sql_handler.delete(self.table_name, conditions=((), [('user_id', '=', user_id)]))

    def drop(self):
        """
            Drop the User table from the database.

            Parameters
            ----------


            Returns
            -------
            Nothing
        """
        self.sql_handler.drop(table_name=self.table_name)

    def store_csv(self, path_file: str = '../../sources/User.csv'):
        """
            Method to store the User table in csv file

            Parameters
            ----------
            path_file : path where save the csv file

            Returns
            -------
            Nothing
        """
        self.sql_handler.store(self.table_name, path_file)

    def column_value_already_used(self, column_name: str, column_value, ignore: bool = False):
        """
            Method to check if a certain value for a column was already used.

            Parameters
            ----------
            column_name : name of the target column

            column_value : value to check if it is already present or not

            ignore : Ignore warning if True, otherwise don't ignore it

            Returns
            -------
            bool : True if value already exist, False otherwise
        """
        if self.sql_handler.column_not_exist('USERS', column_name):
            return True
        if column_value in self.search(conditions=((column_name,), [(column_name, '=', column_value)]), ignore=ignore):
            ColumnValueAlreadyExistWarning('USERS', column_name, column_value)
            return True
        return False

    def check_column_value_validity(self, user_id: str, column_name: str):
        """
            Method to check the validity of a certain value, in particular if a certain column exist.

            Parameters
            ----------
            user_id : ID of a certain user

            column_name : name of the column

            Returns
            -------
            bool : True if the column exist, False otherwise
        """
        if self.sql_handler.column_not_exist('USERS', column_name):
            return False
        if self.item_not_exist('USERS', 'user_id', user_id):
            ColumnValueNotExistWarning('USERS', 'user_id', user_id)
            return False
        return True

    def __str__(self):
        return self.sql_handler.print(self.table_name, 'user_id')

    def generator(self, occurrences: int = 100):
        for i in range(1, occurrences):
            username = 'user-{}'.format(i)
            password = 'pass-{}'.format(i)
            email = username + '@gmail.com'
            country = 'country' if random.choice([True, False]) else None
            self.add(username, password, email, country, ignore=True)


if __name__ == '__main__':
    users = UserTable(username='Pietro', password='pwd', email='pietro.admin@gmail.com')
    # users = UserTable()
    users.column_value_already_used('username', 'Pietro')
    print(users.search((('email', ), [('user_id', '=', '0')])))
    users.add('Pietro', 'Ciccio', 'pierpa.m.96@gmail.com', 'Italy')
    users.add('Franco', 'Ciccio', 'pierpa.m.96@gmail.com')
    print(users.search((('username', ), [('user_id', '=', '0')])))
    users.update('0', 'password', 'Pasticcio')
    users.remove('1')
    users.add('Franco', 'Ciccio', 'pierpa.m.96@gmail.com')
    print(users)
    # users.store_csv()

    # users.generator(1000)
    # users.store_csv()
