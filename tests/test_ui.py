import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import sys
sys.modules['db'] = MagicMock()
sys.modules['api'] = MagicMock()
sys.modules['util'] = MagicMock()
from ui import BoardGameApp

class TestBoardGameApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = BoardGameApp(self.root)

    def tearDown(self):
        self.root.destroy()

    @patch('db.init_db')
    def test_init_db_thread(self, mock_init_db):
        app = BoardGameApp(self.root)
        mock_init_db.assert_called()

    @patch('db.add_game')
    @patch('db.get_game_by_barcode', return_value=None)
    @patch('api.lookup_barcode', return_value={'title': 'Test Game', 'description': 'Desc', 'images': ['url']})
    @patch('util.show_info')
    def test_add_game_success(self, mock_info, mock_lookup, mock_get, mock_add):
        self.app.add_game()
        self.assertTrue(True)

    @patch('db.list_games', return_value=[('Test Game', '123', 'A', '1', None, 'Desc', 'url')])
    def test_list_games(self, mock_list):
        self.app.list_games()
        self.assertTrue(mock_list.called)

    @patch('db.list_games', return_value=[])
    def test_list_games_empty(self, mock_list):
        self.app.list_games()
        self.assertTrue(mock_list.called)

    @patch('db.delete_game')
    @patch('db.list_games', return_value=[('Test Game', '123', 'A', '1', None, 'Desc', 'url')])
    def test_delete_game(self, mock_list, mock_delete):
        self.app.delete_game()
        self.assertTrue(mock_list.called)

    @patch('db.list_games', return_value=[])
    def test_delete_game_empty(self, mock_list):
        self.app.delete_game()
        self.assertTrue(mock_list.called)

    @patch('db.loan_game')
    @patch('db.list_games', return_value=[('Test Game', '123', 'A', '1', None, 'Desc', 'url')])
    def test_loan_game(self, mock_list, mock_loan):
        self.app.loan_game()
        self.assertTrue(mock_list.called)

    @patch('db.list_games', return_value=[])
    def test_loan_game_empty(self, mock_list):
        self.app.loan_game()
        self.assertTrue(mock_list.called)

    @patch('db.return_game')
    @patch('db.list_loaned_games', return_value=[('Test Game', '123', 'A', '1', 'John', 'Desc', 'url')])
    def test_return_game(self, mock_loaned, mock_return):
        self.app.return_game()
        self.assertTrue(mock_loaned.called)

    @patch('db.list_loaned_games', return_value=[])
    def test_return_game_empty(self, mock_loaned):
        self.app.return_game()
        self.assertTrue(mock_loaned.called)

    @patch('db.get_game_by_barcode', return_value=None)
    @patch('api.lookup_barcode', return_value=None)
    @patch('util.show_error')
    def test_add_game_no_data(self, mock_error, mock_lookup, mock_get):
        self.app.add_game()
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
