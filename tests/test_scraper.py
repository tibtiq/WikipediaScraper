from unittest.mock import patch

from bs4 import BeautifulSoup

from wikipediascraper.scraper import digest_page, scrape_wiki_page


@patch("wikipediascraper.scraper.load_section")
@patch("wikipediascraper.scraper.load_page")
def test_scrape_wiki_page(mock_load_page, mock_load_section):
    mock_load_page.return_value = [
        {"line": "History", "index": "1"},
        {"line": "Overview", "index": "2"},
    ]
    html_section_1 = """
    <p>
        Google was founded in 1998 [1].
        Check out <a href="/wiki/Larry_Page">Larry Page</a>
        and <a href="#cite_note-1">[1]</a>.
    </p>
    """
    html_section_2 = "<p>Overview text here.</p>"
    mock_load_section.side_effect = [
        BeautifulSoup(html_section_1, "html.parser"),
        BeautifulSoup(html_section_2, "html.parser"),
    ]

    url = "https://en.wikipedia.org/wiki/Google"
    result = scrape_wiki_page(url)

    mock_load_page.assert_called_once_with("Google")
    assert mock_load_section.call_count == 2
    mock_load_section.assert_any_call("1", "Google")
    mock_load_section.assert_any_call("2", "Google")

    assert len(result) == 2
    sec1 = result[0]
    assert sec1["title"] == "History"
    assert sec1["index"] == "1"
    assert "[1]" not in sec1["text"]
    assert "Google was founded in 1998" in sec1["text"]
    assert sec1["hyperlinks"] == ["https://en.wikipedia.org//wiki/Larry_Page"]
    sec2 = result[1]
    assert sec2["title"] == "Overview"
    assert sec2["text"] == "Overview text here."


class TestDigestPage:
    @patch("wikipediascraper.scraper.stopwords.words")
    def test_success(self, mock_stopwords):
        mock_stopwords.return_value = ["is", "a", "and", "the"]
        input_sections = [
            {
                "title": "Introduction",
                "index": "1",
                "text": "Python is a language, and Python is great.",
                "hyperlinks": [],
            }
        ]

        result = digest_page(input_sections)

        sec = result[0]
        assert "frequencies" in sec
        expected_freqs = {
            "python": 2,
            "language": 1,
            "great": 1,
        }
        assert sec["frequencies"] == expected_freqs

    @patch("wikipediascraper.scraper.stopwords.words")
    def test_all_puncuation(self, mock_stopwords):
        mock_stopwords.return_value = ["is", "a", "and", "the"]
        input_sections = [
            {
                "title": "Introduction",
                "index": "1",
                "text": "\"Python\" is a language! 'Python' is great.",
                "hyperlinks": [],
            }
        ]

        result = digest_page(input_sections)

        sec = result[0]
        assert "frequencies" in sec
        expected_freqs = {
            "python": 2,
            "language": 1,
            "great": 1,
        }
        assert sec["frequencies"] == expected_freqs

    @patch("wikipediascraper.scraper.stopwords.words")
    def test_empty_text(self, mock_stopwords):
        mock_stopwords.return_value = ["the"]
        input_sections = [
            {"title": "Empty", "index": "1", "text": "", "hyperlinks": []}
        ]

        result = digest_page(input_sections)

        assert result[0]["frequencies"] == {}
