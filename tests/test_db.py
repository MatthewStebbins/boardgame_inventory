import unittest
from unittest.mock import patch
import db

class TestDb(unittest.TestCase):
    @patch('db.sqlite3.connect')
    def test_init_db(self, mock_connect):
        db.init_db()
        self.assertTrue(mock_connect.called)

    @patch('db.sqlite3.connect')
    def test_add_game(self, mock_connect):
        db.add_game('Test', '123', 'A', '1', 'desc', 'img')
        self.assertTrue(mock_connect.called)

    @patch('db.sqlite3.connect')
    def test_get_game_by_barcode(self, mock_connect):
        db.get_game_by_barcode('123')
        self.assertTrue(mock_connect.called)

    @patch('db.sqlite3.connect')
    def test_delete_game(self, mock_connect):
        db.delete_game('123')
        self.assertTrue(mock_connect.called)

    @patch('db.sqlite3.connect')
    def test_loan_game(self, mock_connect):
        db.loan_game('123', 'John')
        self.assertTrue(mock_connect.called)

    @patch('db.sqlite3.connect')
    def test_return_game(self, mock_connect):
        db.return_game('123')
        self.assertTrue(mock_connect.called)

    @patch('db.sqlite3.connect')
    def test_update_game_location(self, mock_connect):
        db.update_game_location('123', 'A', '1')
        self.assertTrue(mock_connect.called)

    @patch('db.sqlite3.connect')
    def test_list_loaned_games(self, mock_connect):
        db.list_loaned_games()
        self.assertTrue(mock_connect.called)

if __name__ == '__main__':
    unittest.main()
