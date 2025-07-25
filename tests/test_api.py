import unittest
from unittest.mock import patch
import api

class TestApi(unittest.TestCase):
    @patch('api.requests.get')
    def test_lookup_barcode_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'product': {
                'title': 'Test',
                'description': 'desc',
                'images': ['img']
            }
        }
        result = api.lookup_barcode('123')
        self.assertEqual(result['title'], 'Test')
        self.assertEqual(result['description'], 'desc')
        self.assertEqual(result['images'], ['img'])

    @patch('api.requests.get')
    def test_lookup_barcode_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        result = api.lookup_barcode('123')
        self.assertIsNone(result)

    @patch('api.requests.get', side_effect=Exception('API error'))
    def test_lookup_barcode_exception(self, mock_get):
        result = api.lookup_barcode('123')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
