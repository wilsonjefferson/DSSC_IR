import unittest
from core.data_handlers.UserTable import UserTable
from parameterized import parameterized

from exceptions.ColumnValueException import ColumnValueNotExistException
from exceptions.sql_handler.sql_handler_exceptions.ColumnNameException import ColumnNameNotExistException


class UserTableTest(unittest.TestCase):

    def tearDown(self):
        self.users.drop()

    def setUp(self):
        self.users = UserTable()

    @parameterized.expand([
        ('UserTableTest_Test_01', '0', False),
        ('UserTableTest_Test_02', '1', True)
    ])
    def test_user_not_exist(self, _, test_user_id, expected):
        self.assertEqual(expected, self.users.item_not_exist('USERS', 'user_id', test_user_id))

    @parameterized.expand([
        ('UserTableTest_Test_03', '0', 'username', True)
    ])
    def test_check_column_value_validity(self, _, test_user_id, test_column_name, expected):
        self.assertEqual(expected, self.users.check_column_value_validity(test_user_id, test_column_name))
    
    @parameterized.expand([
        ('UserTableTest_Test_04', ColumnNameNotExistException, '0', 'Weight'),
        ('UserTableTest_Test_05', ColumnValueNotExistException, '1', 'username')
    ])
    @unittest.skip('Exception no more raised')
    def test_check_column_value_validity2(self, _, test_exception, test_user_id, test_column_name):
        self.assertRaises(test_exception, self.users.check_column_value_validity, test_user_id, test_column_name)

    @parameterized.expand([
        ('UserTableTest_Test_07', '0', 'username', 'admin1', 'admin1')
    ])
    def test_update_user(self, _, test_user_id, test_column_name, test_new_column_value, expected):
        self.users.update(test_user_id, test_column_name, test_new_column_value)
        new_column_value = self.users.search(conditions=((test_column_name,), [('user_id', '=', test_user_id)]))
        self.assertEqual(expected, new_column_value)

    @parameterized.expand([
        ('UserTableTest_Test_08', 'username', 'admin', True),
        ('UserTableTest_Test_09', 'username', 'Franco', False)
    ])
    def test_column_value_already_used(self, _, test_column_name, test_column_value, expected):
        self.assertEqual(expected, self.users.column_value_already_used(test_column_name, test_column_value))

    @parameterized.expand([
        ('UserTableTest_Test_10', 'Weight', 'admin', ColumnNameNotExistException)
    ])
    @unittest.skip('Exception no more raised')
    def test_column_value_already_used2(self, _, test_column_name, test_column_value, test_exception):
        self.assertRaises(test_exception, self.users.column_value_already_used, test_column_name, test_column_value)


if __name__ == '__main__':
    unittest.main()
