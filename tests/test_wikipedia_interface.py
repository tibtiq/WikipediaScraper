from unittest.mock import MagicMock, patch

import pytest
import requests
from bs4 import BeautifulSoup

from wikipediascraper.wikipedia_interface import HEADERS, load_page, load_section


class TestLoadPage:
    @patch("wikipediascraper.wikipedia_interface.requests.get")
    def test_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "parse": {
                "tocdata": {
                    "sections": [
                        {"toclevel": 1, "line": "History", "number": "1"},
                        {"toclevel": 1, "line": "References", "number": "2"},
                    ]
                }
            }
        }
        mock_get.return_value = mock_response

        page_name = "Python_(programming_language)"
        result = load_page(page_name)

        expected_url = f"https://en.wikipedia.org/w/api.php?action=parse&prop=tocdata&format=json&page={page_name}"
        mock_get.assert_called_once_with(expected_url, headers=HEADERS)

        assert len(result) == 2
        assert result[0]["line"] == "History"
        assert result[1]["line"] == "References"

    @patch("wikipediascraper.wikipedia_interface.requests.get")
    def test_missing_key_raises_key_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {
                "code": "missingtitle",
                "info": "The page you specified doesn't exist.",
            }
        }
        mock_get.return_value = mock_response

        with pytest.raises(KeyError):
            load_page("NonExistentPage12345")


class TestLoadSection:
    @patch("wikipediascraper.wikipedia_interface.requests.get")
    def test_success(self, mock_get):
        mock_response = MagicMock()
        mock_html = "<div class='mw-parser-output'><p>Python is a programming language.</p></div>"
        mock_response.json.return_value = {"parse": {"text": {"*": mock_html}}}
        mock_get.return_value = mock_response

        section_index = 2
        page_name = "Python_(programming_language)"
        result = load_section(section_index, page_name)

        expected_url = f"https://en.wikipedia.org/w/api.php?action=parse&section={section_index}&prop=text&format=json&page={page_name}"
        mock_get.assert_called_once_with(expected_url, headers=HEADERS)
        mock_response.raise_for_status.assert_called_once()

        assert isinstance(result, BeautifulSoup)
        assert result.find("p").text == "Python is a programming language."

    @patch("wikipediascraper.wikipedia_interface.requests.get")
    def test_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error"
        )
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            load_section(1, "NonExistentPage")

    @patch("wikipediascraper.wikipedia_interface.requests.get")
    def test_malformed_json_raises_key_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {"code": "nosuchsection", "info": "There is no section 999"}
        }
        mock_get.return_value = mock_response

        with pytest.raises(KeyError):
            load_section(999, "Python_(programming_language)")


@pytest.mark.integration
def test_load_page_real_wikipedia_api():
    page_name = "Python_(programming_language)"

    result = load_page(page_name)

    assert isinstance(result, list)
    assert len(result) > 0
    assert any(section.get("line") == "Syntax and semantics" for section in result)
