import unittest
import config

class TestConfig(unittest.TestCase):
    def test_api_key_exists(self):
        self.assertTrue(hasattr(config, 'API_KEY'))
        self.assertIsInstance(config.API_KEY, str)

    def test_api_url_exists(self):
        self.assertTrue(hasattr(config, 'API_URL'))
        self.assertIsInstance(config.API_URL, str)

if __name__ == '__main__':
    unittest.main()
