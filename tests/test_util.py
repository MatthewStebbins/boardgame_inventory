import unittest
from util import validate_location_barcode, show_info, show_error, confirm_action
import tkinter as tk

class TestUtil(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.entry = tk.Entry(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_validate_location_barcode_valid(self):
        bookcase, shelf = validate_location_barcode('A-1')
        self.assertEqual(bookcase, 'A')
        self.assertEqual(shelf, '1')

    def test_validate_location_barcode_invalid(self):
        bookcase, shelf = validate_location_barcode('A1')
        self.assertIsNone(bookcase)
        self.assertIsNone(shelf)

    def test_update_entry(self):
        from util import update_entry
        update_entry(self.entry, 'test')
        self.assertEqual(self.entry.get(), 'test')

if __name__ == '__main__':
    unittest.main()
