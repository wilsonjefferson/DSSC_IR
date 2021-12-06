import unittest
from core.data_handlers.SongTable import SongTable
from core.data_handlers.UserTable import UserTable
from parameterized import parameterized, parameterized_class
from core.data_handlers.HistoryTable import HistoryTable
from exceptions.ColumnValueException import ColumnValueException, ColumnValueNotExistException
from exceptions.sql_handler.sql_handler_exceptions.ColumnNameException import ColumnNameNotExistException

# @parameterized_class(('init_user_id', 'init_song_id', 'test_user_id', 'expected'), [
#         ('0', '0', '0', False),
#         ('0', None, '1', True)
#     ])


@parameterized_class(('init_user_id', 'init_song_id'), [
        ('0', '0')
])
class HistoryTableTest(unittest.TestCase):

    def tearDown(self):
        self.history.drop()
        self.users.drop()
        self.songs.drop()

    def setUp(self):
        self.users = UserTable()
        self.users.add('Pietro', 'Ciccio1', 'pietro.m.96@gmail.com', 'Italy')
        self.users.add('Pierre', 'Ciccio2', 'pierre.m.96@gmail.com', 'France')
        self.songs = SongTable('../sources/processed_data/spotify_music/SpotifyFeatures.csv')
        self.history = HistoryTable(self.init_user_id, self.init_song_id)

    @parameterized.expand([
        ('HistoryTableTest_Test_01', '0', False),
        ('HistoryTableTest_Test_02', '1', True)
    ])
    def test_item_not_exist(self, _, test_user_id, expected):
        self.assertEqual(expected, self.history.item_not_exist('HISTORY', 'user_id', test_user_id))

    @parameterized.expand([
        ('HistoryTableTest_Test_03', '0', '0', False),
        ('HistoryTableTest_Test_04', '0', '1', True)
    ])
    def test_song_not_listened_by_user(self, _, test_user_id, test_song_id, expected):
        self.assertEqual(expected, self.history.song_not_listened_by_user(test_user_id, test_song_id))

    @parameterized.expand([
        ('HistoryTableTest_Test_05', '0', '0', False),
        ('HistoryTableTest_Test_06', '0', '1', True)
    ])
    def test_song_not_listened_by_user(self, _, test_user_id, test_song_id, expected):
        self.assertEqual(expected, self.history.song_not_listened_by_user(test_user_id, test_song_id))

    @parameterized.expand([
        ('HistoryTableTest_Test_07', '0', '1', 1),
        ('HistoryTableTest_Test_08', '0', '2', 1)
    ])
    def test_add_song(self, _, test_user_id, test_song_id, expected):
        self.assertEqual(expected, self.history.add(test_user_id, test_song_id))

    @parameterized.expand([
        ('HistoryTableTest_Test_09', '1', '3', ColumnValueNotExistException)
    ])
    @unittest.skip('Exception no more raised')
    def test_add_song2(self, _, test_user_id, test_song_id, test_exception):
        self.assertRaises(test_exception, self.history.add, test_user_id, test_song_id)

    @parameterized.expand([
        ('HistoryTableTest_Test_10', '0', '0', 2),
        ('HistoryTableTest_Test_11', '0', '1', 1)
    ])
    def test_update_song(self, _, test_user_id, test_song_id, expected):
        self.history.update(test_user_id, test_song_id)
        actual = self.history.search((('repetition', ), [('user_id', '=', test_user_id), 'AND',
                                                         ('song_id', '=', test_song_id)]))
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ('HistoryTableTest_Test_12', '1', '3', ColumnValueNotExistException)
    ])
    @unittest.skip('Exception no more raised')
    def test_update_song2(self, _, test_user_id, test_song_id, test_exception):
        self.assertRaises(test_exception, self.history.update, test_user_id, test_song_id)

    @parameterized.expand([
        ('HistoryTableTest_Test_15', '0', '0', 'Time', ColumnNameNotExistException),
        ('HistoryTableTest_Test_16', '1', '0', 'repetition', ColumnValueException),
        ('HistoryTableTest_Test_17', '0', '1', 'repetition', ColumnValueException)
    ])
    @unittest.skip('Exception no more raised: substituted by Warning message')
    def test_get_column_value_song2(self, _, test_user_id, test_song_id, test_column_name, test_exception):
        pass


if __name__ == '__main__':
    unittest.main()
