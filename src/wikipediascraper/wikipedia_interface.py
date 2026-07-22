import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Wikipedia-Scrapper (https://github.com/tibtiq/Wikipedia-Scraper; 29826331+tibtiq@users.noreply.github.com)"
}


def load_page(page_name: str) -> dict:
    """Load section data from Wikipedia artcle.

    Args:
        page_name (str): Wikipedia page name.

    Returns:
        page (dict): A dict structure containing section data for a wikipedia page.
    """
    response = requests.get(
        f"https://en.wikipedia.org/w/api.php?action=parse&prop=tocdata&format=json&page={page_name}",
        headers=HEADERS,
    )

    # todo use a dataclass
    page = response.json()["parse"]["tocdata"]["sections"]

    return page


def load_section(section_index: int, page_name: str) -> BeautifulSoup:
    """Load and parse section text from Wikipedia artcle.

    Args:
        section_index (int): Index of section within wikipedia page.
        page_name (str): Wikipedia page name.

    Returns:
        BeautifulSoup: A data structure representing a parsed HTML or XML document.
    """
    response = requests.get(
        f"https://en.wikipedia.org/w/api.php?action=parse&section={section_index}&prop=text&format=json&page={page_name}",
        headers=HEADERS,
    )

    response = response.json()["parse"]["text"]["*"]
    parsed_html = BeautifulSoup(response, features="lxml")

    return parsed_html
