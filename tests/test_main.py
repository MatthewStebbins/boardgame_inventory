import unittest
from unittest.mock import patch
import main

class TestMain(unittest.TestCase):
    @patch('main.tk.Tk')
    @patch('main.BoardGameApp')
    def test_main_runs(self, mock_app, mock_tk):
        with patch('main.__name__', '__main__'):
            main.__file__ = 'main.py'
            try:
                exec(open('main.py').read())
            except Exception:
                pass
        self.assertTrue(mock_tk.called)
        self.assertTrue(mock_app.called)

if __name__ == '__main__':
    unittest.main()
