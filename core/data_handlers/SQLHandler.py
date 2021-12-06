import csv
import sqlite3
from sqlite3 import Error
from unidecode import unidecode

from exceptions.sql_handler.sql_handler_exceptions.AlterActionNotExistException import AlterActionNotExistException
from exceptions.sql_handler.sql_handler_exceptions.ColumnNameException import ColumnNameNotExistException, \
    ColumnNameAlreadyExistException
from exceptions.sql_handler.sql_handler_warning.TableWarning import TableAlreadyExistWarning
from exceptions.sql_handler.sql_handler_warning.TableWarning import TableNotExistWarning
from exceptions.sql_handler.sql_handler_exceptions.SQLException import SQLException
from exceptions.sql_handler.sql_handler_exceptions.TableException import TableNotExistException


class SQLHandler:
    """
        This class interact with the database through sql queries.

        It is a critical class, since most of the other classes use this
        class to interact with the database.

        Parameters
        ----------
        db_file : path where find the database
    """

    def __init__(self, db_file: str):
        self.connection = None
        try:
            self.connection = sqlite3.connect(db_file)
            self.connection.execute("PRAGMA foreign_keys = on")
            print(sqlite3.version)
        except Error as e:
            print(e)

    def __del__(self):
        if self.connection:
            self.connection.close()

    def create(self, sql: str):
        """
            Create a new table in the database.

            Parameters
            ----------
            sql : ddl-dql query defining the new table

            Returns
            -------
            Nothing
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(e)

    def drop(self, table_name: str):
        """
            Drop an existing table in the database.

            Parameters
            ----------
            table_name : name of the table

            Returns
            -------
            Nothing
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute('DROP TABLE ' + table_name)
            self.connection.commit()
        except sqlite3.Error as exception:
            print(exception)
        finally:
            cursor.close()

    def insert(self, table_name: str, data, sql: str = None, ignore_warning: bool = False):
        """
            Insert a new row in a specific table, it can be done directly providing the sql query
            or just by means of giving the data.

            Parameters
            ----------
            table_name : name of the table

            data : information to be inserted in the table

            sql : query mode to insert a new row

            ignore_warning : binary variable to decide if an eventual warning have to be silenced

            Returns
            -------
            rec_songs : list of recommended songs by ID
        """
        if not self.exist(table_name, ignore_warning):
            return

        if sql is None:
            columns = self.columns_of(table_name)
            variables = str('?, ' * len(columns))[:-2]
            columns_string = str(columns).strip('[]').replace("'", "")
            sql = 'INSERT INTO ' + table_name + '(' + columns_string + ') VALUES(' + variables + ')'

        cursor = self.connection.cursor()

        if isinstance(data, tuple) or isinstance(data, str):
            if isinstance(data, tuple):
                data = self.unicode_conversion(data)
            cursor.execute(sql, data)
        else:
            cursor.executemany(sql, data)
        self.connection.commit()
        return cursor.lastrowid

    def update(self, table_name: str, conditions: tuple = None, sql: str = None, data: tuple = None):
        """
            Update a row(s) of an existing table.

            Parameters
            ----------
            table_name : name of the table

            conditions : essential information to build the sql query ((<column_name>), [(column_name, opt, value)])

            sql : query mode to update a row(s) in the table

            data : information to update

            Returns
            -------
            rec_songs : list of recommended songs by ID
        """
        cursor = self.connection.cursor()
        self.sql_operation_handler(table_name, cursor, 'UPDATE', conditions, sql, data)
        self.connection.commit()
        cursor.close()

    def delete(self, table_name: str, conditions: tuple = None, sql: str = None, data: tuple = None):
        """
            Delete a row(s) of an existing table.

            Parameters
            ----------
            table_name : name of the table

            conditions : essential information to build the sql query ((<column_name>), [(column_name, opt, value)])

            sql : query mode to update a row(s) in the table

            data : information to delete

            Returns
            -------
            Nothing
        """
        cursor = self.connection.cursor()
        try:
            self.sql_operation_handler(table_name, cursor, 'DELETE', conditions, sql, data)
            self.connection.commit()
        except sqlite3.Error as exception:
            print(exception)
        cursor.close()

    def search(self, table_name: str = None, conditions: tuple = None, sql: str = None, data: tuple = None, flat: bool = True):
        """
            Search a row(s) of an existing table.

            Parameters
            ----------
            table_name : name of the table

            conditions : essential information to build the sql query ((<column_name>), [(column_name, opt, value)])

            sql : query mode to search a row(s) in the table

            data : information to search

            flat : flat row if True, otherwise don't flat it

            Returns
            -------
            rows : resulting tuple from the sql query
        """
        cursor = self.connection.cursor()
        self.sql_operation_handler(table_name, cursor, 'SELECT', conditions, sql, data)
        rows = cursor.fetchall()  # list of tuples
        cursor.close()

        if len(rows) == 1 and len(rows[0]) == 1:
            return rows[0][0]
        elif len(rows) == 1 and flat:
            return [item for item in rows[0]]
        else:
            return rows

    def is_empty(self, table_name: str):
        rows = self.search(table_name, sql='SELECT * FROM ' + table_name)
        return True if len(rows) == 0 else False

    def sql_operation_handler(self, table_name: str, cursor, sql_opt: str, conditions: tuple = None, sql: str = None, data: tuple = None):
        """
            Support method to handle the right sql operation according the inputs given.

            Parameters
            ----------
            table_name : name of the table

            cursor : cursor object used to interact with the database

            sql_opt : kind of sql operation to be performed (SELECT, UPDATE, DELETE, ...)

            conditions : essential information to build the sql query ((<column_name>), [(column_name, opt, value)])

            sql : query mode to update a row(s) in the table

            data : information to delete

            Returns
            -------
            Nothing
        """
        if conditions and not sql and data is None:
            sql, values = self.build_query(table_name, sql_opt, conditions)
            # print(sql, values)
            try:
                cursor.execute(sql, values)
            except sqlite3.Error as exception:
                print(exception)
        elif not conditions and sql and data:
            try:
                cursor.execute(sql, data)
            except sqlite3.Error as exception:
                print(exception)
        elif not conditions and sql and data is None:
            try:
                cursor.execute(sql)
            except sqlite3.Error as exception:
                print(exception)
        else:
            raise SQLException("ERROR: sql_operation_handler's inputs are not well defined.")

    # conditions = (<target columns>, <conditions for WHERE>)
    # conditions = ((<target columns>), [(condition1), operator, (condition2), ...])
    def build_query(self, table_name: str, query_opt: str, conditions: tuple):
        """
            Support method to build up the query if the "conditions" and "data" are given.

            Parameters
            ----------
            table_name : name of the table

            conditions : essential information to build the sql query ((<column_name>), [(column_name, opt, value)])

            query_opt : kind of sql operation to be performed (SELECT, UPDATE, DELETE, ...)

            Returns
            -------
            sql, values : the sql query and the data related to the query
        """
        str_condition = ''
        values = []
        for condition in conditions[1]:
            if type(condition) == tuple:
                column, operator, value = condition
                str_condition += column + ' ' + operator + ' ? '
                values.append(value)
            else:
                str_condition += condition + ' '

        if query_opt == 'SELECT':
            str_targets = ''.join(column + ', ' for column in conditions[0])[:-2]
            if str_condition:
                sql = 'SELECT ' + str_targets + ' FROM ' + table_name + ' WHERE ' + str_condition
            else:
                sql = 'SELECT ' + str_targets + ' FROM ' + table_name
        elif query_opt == 'DELETE':
            sql = 'DELETE FROM ' + table_name + ' WHERE ' + str_condition
        elif query_opt == 'UPDATE':
            str_targets = ''
            set_value = []
            if len(conditions[0]) > 2:  # it is a tuple of tuples
                for condition in conditions[0]:
                    column, value = condition
                    str_targets += column + ' = ?, '
                    set_value.append(value)
                str_targets = str_targets[:-2]
            else:  # it is a single tuple
                str_targets += conditions[0][0] + ' = ?'
                set_value.append(conditions[0][1])
            values = set_value + values
            sql = 'UPDATE ' + table_name + ' SET ' + str_targets + ' WHERE ' + str_condition
        else:
            raise SQLException("ERROR: query_opt = {} in build_query method is not acceptable.".format(query_opt))

        values = tuple(values)
        return sql, values

    def alter(self, table_name: str, action: str, parameters):
        """
            Alter the actual status of the given table.

            Parameters
            ----------
            table_name : name of the table

            action : what kind of alteration is requested (RENAME TO, ADD COLUMN, RENAME COLUMN)

            parameters : values for the alteration

            Returns
            -------
            Nothing
        """
        if not self.exist(table_name):
            return

        sql = 'ALTER TABLE ' + table_name
        if action == 'rename':
            sql += ' RENAME TO ' + parameters
        elif action == 'add_column':
            if parameters in self.columns_of(table_name):
                raise ColumnNameAlreadyExistException(table_name, parameters)
            sql += ' ADD COLUMN ' + parameters
        elif action == 'rename_column':
            sql += ' RENAME COLUMN ' + parameters[0] + ' TO ' + parameters[1]
        else:
            raise AlterActionNotExistException(action)

        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.Error as exception:
            print(exception)
        cursor.close()

    def exist(self, table_name: str, ignore_warning: bool = False):
        """
            Support method to handle the right sql operation according the inputs given.

            Parameters
            ----------
            table_name : name of the table

            ignore_warning : binary variable to set the warning silenced

            Returns
            -------
            Bool : True if the table exist, False if table does not exist
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type = 'table' AND name = ?", (table_name,))
        self.connection.commit()
        if cursor.fetchone()[0] == 1:
            return True
        TableNotExistWarning(table_name, ignore_warning)
        return False

    def columns_of(self, table_name: str, ignore_warning: bool = False):
        """
            Method providing the columns name of a given table.

            Parameters
            ----------
            table_name : name of the table

            ignore_warning : binary variable to set the warning silenced

            Returns
            -------
            list : set of columns names
        """
        if not self.exist(table_name, ignore_warning):
            return
        cursor = self.connection.cursor()
        table_data = cursor.execute('SELECT * FROM ' + table_name)
        cursor.close()
        return [column[0] for column in table_data.description]

    def unicode_conversion(self, data):
        """
            Support method to convert every entry in a unicode format to avoid any issues.

            Parameters
            ----------
            data : values to be formatted

            Returns
            -------
            row : set of formatted data
        """
        row = ()
        for feature in data:
            row += (unidecode(str(feature)),)
        return row

    def store(self, table_name: str, path_file: str, separator: str = '\t'):
        """
            Store the given table in csv file.

            Parameters
            ----------
            table_name : name of the table

            path_file : path where to store the csv table file

            separator : kind of separator to use in the csv file

            Returns
            -------
            Nothing
        """
        if not self.exist(table_name, True):
            raise TableNotExistException(table_name)

        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM ' + table_name)
        with open(path_file, 'w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=separator)
            columns = [i[0] for i in cursor.description]
            csv_writer.writerow(columns)

            # since some datasets are the header as first row we have
            # to check it to avoid to insert it in the csv file

            potential_columns = cursor.fetchone()
            if list(potential_columns) != columns:
                csv_writer.writerow(potential_columns)
            for features in cursor.fetchall():
                csv_writer.writerow(features)
            cursor.close()

    def load(self, table_name: str, sql: str, path_file: str, separator: str = '\t'):
        """
            Load an existing csv table in the database.

            Parameters
            ----------
            table_name : name of the table

            sql : sql-ddl query to create the table in the database

            path_file : path where find the csv file

            separator : kind of separator used in the csv file

            Returns
            -------
            Nothing
        """
        if self.exist(table_name, True):
            TableAlreadyExistWarning(table_name, False)
        else:
            self.create(sql)
            columns = self.columns_of(table_name, ignore_warning=True)
            with open(file=path_file, mode='r', encoding='utf-8', newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=separator)
                potential_columns = next(csv_reader)
                if type(potential_columns) != list:
                    if list(potential_columns) != columns:
                        self.insert(table_name, potential_columns, ignore_warning=True)
                else:
                    if potential_columns != columns:
                        self.insert(table_name, potential_columns, ignore_warning=True)

                self.insert(table_name=table_name, data=csv_reader, ignore_warning=True)

    def select_columns(self, table_name: str, data_types: list):
        """
            Methods to get detailed information about columns of a given table.

            Parameters
            ----------
            table_name : name of the table

            data_types : used to filter the columns according their data type

            Returns
            -------
            columns : list of columns
        """
        if not self.exist(table_name, True):
            raise TableNotExistException(table_name)
        cursor = self.connection.cursor()
        cursor.execute('PRAGMA table_info({})'.format(table_name))
        rows = cursor.fetchall()
        columns = []
        for row in rows:
            for data_type in data_types:
                if data_type in row:
                    columns.append(row[1])
        cursor.close()
        return columns

    def print(self, table_name: str, column_name: str):
        """
            print a table according a column order

            Parameters
            ----------
            table_name : name of the table

            column_name : column by which order the printing

            Returns
            -------
            Nothing
        """
        if not self.exist(table_name, True):
            raise TableNotExistException(table_name)
        if self.column_not_exist(table_name, column_name):
            raise ColumnNameNotExistException(table_name, column_name)

        # This method provide an order print version of the table
        # but actually the table is not ordered inplace
        columns = self.columns_of(table_name)
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM ' + table_name + ' ORDER BY ' + column_name)
        rows = cursor.fetchall()
        cursor.close()
        str_table = ''.join([str(row) + '\n' for row in rows])[:-1]
        return str(columns) + '\n' + str_table

    def column_not_exist(self, table_name: str, column_name: str):
        """
            Method to check if a certain column exist in a given table.

            Parameters
            ----------
            table_name : name of the table

            column_name : name of a column

            Returns
            -------
            bool : True if the column exist, False otherwise
        """
        if column_name not in self.columns_of(table_name):
            return True
        else:
            return False


if __name__ == '__main__':
    sql_handler = SQLHandler(r'../../sources/user_dataset.db')
    sql_ddl = """CREATE TABLE IF NOT EXISTS TASKS (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    priority integer,
                                    status_id integer NOT NULL,
                                    project_id integer NOT NULL,
                                    begin_date text NOT NULL,
                                    end_date text NOT NULL
                                );"""

    # sql_handler.create(sql_ddl)
    # print(sql_handler.exist('TASKS'))
    # print(sql_handler.columns_of('TASKS'))
    # sql_handler.insert('TASKS', (1, 'Task1', 1, 1, 1, '2015-01-01', '2015-01-02'))
    # sql_handler.insert('TASKS', (2, 'Task', 2, 2, 2, '2015-01-01', '2015-01-02'))
    # sql_handler.insert('TASKS', (3, 'Task', 3, 3, 3, '2015-01-01', '2015-01-02'))
    # print(sql_handler.search('TASKS', conditions=(('project_id', 'begin_date', 'end_date'), [('id', '=', 1), 'OR', ('id', '>', 2)])))
    # sql_handler.update('TASKS', conditions=((('priority', 2), ('begin_date', '2015-01-04'), ('end_date', '2015-01-06')), [('id', '=', 1)]))
    # sql_handler.delete('TASKS', conditions=((), [('id', '=', 1), 'OR', ('id', '>', 2)]))
    # sql_handler.drop('TASKS')
    #print(sql_handler.search(table_name='TASKS', conditions=(('id', 'status_id', 'project_id'), [('name', '=', 'Task')])))
    # print(sql_handler.search('TASKS', sql='SELECT id FROM TASKS WHERE id=2'))
    #sql_handler.store('TASKS', r'../../sources/Tasks.csv')
    # sql_handler.load(table_name='TASKS', sql=sql_ddl, path_file=r'../../sources/Tasks.csv', separator='\t')
    # sql_handler.alter('TASKS', 'rename', 'Tasks1')
    #sql_handler.alter('Tasks1', 'add_column', 'team_leader')
    # sql_handler.alter('Tasks1', 'rename_column', ['team_leader', 'leader'])
    # print(sql_handler.print('Tasks1', 'id'))
    # sql_handler.drop('Tasks1')
