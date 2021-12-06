import unittest
from parameterized import parameterized
from core.data_handlers.SongTable import SongTable
from exceptions.ColumnValueException import ColumnValueNotExistException
from exceptions.sql_handler.sql_handler_exceptions.ColumnNameException import ColumnNameNotExistException


class SongTableTest(unittest.TestCase):

    def tearDown(self):
        self.songs.drop()

    def setUp(self):
        self.songs = SongTable('../sources/processed_data/spotify_music/SpotifyFeatures.csv')

    @parameterized.expand([
        ('SongTableTest_Test_01', '0BjC1NfoEOOusryehmNudP', False),
        ('SongTableTest_Test_02', '0BRjO6ga9RKCKjfDqeFgW5', True)
    ])
    def test_item_not_exist(self, _, test_song_id, expected):
        self.assertEqual(expected, self.songs.item_not_exist('SONGS', 'song_id', test_song_id))

    @parameterized.expand([
        ('SongTableTest_Test_03', '0BRjO6ga9RKCKjfDqeFgWV', 'artist_name', True)
    ])
    def test_check_column_value_validity(self, _, test_song_id, test_column_name, expected):
        self.assertEqual(expected, self.songs.check_column_value_validity(test_song_id, test_column_name))

    @parameterized.expand([
        ('SongTableTest_Test_04', ColumnNameNotExistException, '0BRjO6ga9RKCKjfDqeFgWV', 'Weight'),
        ('SongTableTest_Test_05', ColumnValueNotExistException, '0BjC1NfoEOOusryehmNuda', 'artist_name')
    ])
    @unittest.skip('Exception no more raised')
    def test_check_column_value_validity2(self, _, test_exception, test_song_id, test_column_name):
        self.assertRaises(test_exception, self.songs.check_column_value_validity, test_song_id, test_column_name)

    @parameterized.expand([
        ('SongTableTest_Test_07', '0BRjO6ga9RKCKjfDqeFgWV', 'artist_name', 'Henri Salvador', 'Henri Salvador')
    ])
    def test_update(self, _, test_song_id, test_column_name, test_new_column_value, expected):
        self.songs.update(test_song_id, test_column_name, test_new_column_value)
        new_column_value = self.songs.search(conditions=((test_column_name,), [('song_id', '=', test_song_id)]))
        self.assertEqual(expected, new_column_value)


if __name__ == '__main__':
    unittest.main()
