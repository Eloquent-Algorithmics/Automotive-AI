import requests
import unittest
from unittest.mock import patch
from automotive_ai._utils._functions import search_google, search_bing


class TestSearchGoogle(unittest.TestCase):
    @patch('requests.get')
    def test_search_google_success(self, mock_get):
        mock_response = {
            "items": [
                {
                    "title": "Example Title",
                    "snippet": "Example description",
                    "link": "http://example.com"
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response

        query = "example query"
        results = search_google(query)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Example Title")
        self.assertEqual(results[0]["description"], "Example description")
        self.assertEqual(results[0]["link"], "http://example.com")

    @patch('requests.get')
    def test_search_google_no_results(self, mock_get):
        mock_response = {}
        mock_get.return_value.json.return_value = mock_response

        query = "example query"
        results = search_google(query)

        self.assertEqual(results, [])

    @patch('requests.get')
    def test_search_google_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException

        query = "example query"
        results = search_google(query)

        self.assertEqual(results, [])

    @patch('requests.get')
    def test_search_google_with_optional_params(self, mock_get):
        mock_response = {
            "items": [
                {
                    "title": "Example Title",
                    "snippet": "Example description",
                    "link": "http://example.com"
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response

        query = "example query"
        fileType = "pdf"
        lr = "lang_en"
        results = search_google(query, fileType=fileType, lr=lr)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Example Title")
        self.assertEqual(results[0]["description"], "Example description")
        self.assertEqual(results[0]["link"], "http://example.com")


class TestSearchBing(unittest.TestCase):
    @patch('requests.get')
    def test_search_bing_success(self, mock_get):
        mock_response = {
            "webPages": {
                "value": [
                    {
                        "name": "Example Title",
                        "snippet": "Example description",
                        "url": "http://example.com"
                    }
                ]
            }
        }
        mock_get.return_value.json.return_value = mock_response

        query = "example query"
        results = search_bing(query)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Example Title")
        self.assertEqual(results[0]["description"], "Example description")
        self.assertEqual(results[0]["link"], "http://example.com")

    @patch('requests.get')
    def test_search_bing_no_results(self, mock_get):
        mock_response = {}
        mock_get.return_value.json.return_value = mock_response

        query = "example query"
        results = search_bing(query)

        self.assertEqual(results, [])

    @patch('requests.get')
    def test_search_bing_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException

        query = "example query"
        results = search_bing(query)

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
