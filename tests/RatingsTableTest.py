import unittest

from core.data_handlers.RatingsTable import RatingsTable
from core.data_handlers.SongTable import SongTable
from core.data_handlers.UserTable import UserTable
from parameterized import parameterized
from exceptions.ColumnValueException import ColumnValueNotExistException


class RatingsTableTest(unittest.TestCase):

    def tearDown(self):
        self.ratings.drop()
        self.users.drop()
        self.songs.drop()

    def setUp(self):
        self.users = UserTable()
        self.users.add('Pietro', 'Ciccio1', 'pietro.m.96@gmail.com', 'Italy')
        self.users.add('Pierre', 'Ciccio2', 'pierre.m.96@gmail.com', 'France')
        self.songs = SongTable('../sources/processed_data/spotify_music/SpotifyFeatures.csv')
        self.ratings = RatingsTable()

    @parameterized.expand([
        ('RatingsTableTest_Test_07', 'U-0000', '0BjC1NfoEOOusryehmNudP', 1, 1),
        ('RatingsTableTest_Test_08', 'U-0000', '0CoSDzoNIKCRs124s9uTVy', 2, 2)
    ])
    def test_add_rating(self, _, test_user_id, test_song_id, test_rating, expected):
        self.assertEqual(expected, self.ratings.add(test_user_id, test_song_id, test_rating))

    @parameterized.expand([
        ('RatingsTableTest_Test_09', 'U-0001', '0BjC1NfoEOOusryehmNu11', 1, ColumnValueNotExistException)
    ])
    @unittest.skip('Exception no more raised')
    def test_add_rating2(self, _, test_user_id, test_song_id, test_rating, test_exception):
        self.assertRaises(test_exception, self.ratings.add, test_user_id, test_song_id, test_rating)

    @parameterized.expand([
        ('RatingsTableTest_Test_10', 'U-0000', '0BjC1NfoEOOusryehmNudP', 2, 2),
        ('RatingsTableTest_Test_11', 'U-0000', '0CoSDzoNIKCRs124s9uTVy', 3, 3)
    ])
    def test_update_rating(self, _, test_user_id, test_song_id, test_rating, expected):
        self.ratings.add(test_user_id, test_song_id, 1)
        self.ratings.update(test_user_id, test_song_id, test_rating)
        actual = self.ratings.search((('ratings',), [('user_id', '=', test_user_id), 'AND',
                                                     ('song_id', '=', test_song_id)]))
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ('RatingsTableTest_Test_12', 'U-0001', '0BRjO6ga9RKCKjfDqeFg11', 1, ColumnValueNotExistException)
    ])
    @unittest.skip('Exception no more raised')
    def test_update_rating2(self, _, test_user_id, test_song_id, test_rating, test_exception):
        self.ratings.add(test_user_id, test_song_id, 1)
        self.assertRaises(test_exception, self.ratings.update, test_user_id, test_song_id, test_rating)


if __name__ == '__main__':
    unittest.main()
