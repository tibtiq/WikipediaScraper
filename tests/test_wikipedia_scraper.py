from wikipedia_scraper.wikipedia_scraper import load_page


def test_load_page():
    url = "https://en.wikipedia.org/wiki/Fergana_(moth)"
    expected_results = {
        "hyperlinks": [
            "https://en.wikipedia.org//wiki/Hadeninae",
            "https://en.wikipedia.org//wiki/Wikipedia:Stub",
            "https://en.wikipedia.org/https://en.wikipedia.org/w/index.php?title=Fergana_(moth)&action=edit",
        ],
        "index": "1",
        "text": " This Hadeninae-related article is a stub. You can help Wikipedia by "
        "adding missing information.",
        "title": "References",
    }

    page = load_page(url)

    assert len(page) == 1
    assert page[0] == expected_results
