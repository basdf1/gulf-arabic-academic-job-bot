import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)


SEARCH_QUERIES = [
    "Arabic Language Lecturer",
    "Arabic Language Assistant Professor",
    "Arabic Language Associate Professor",
    "Arabic Language Professor",
    "محاضر لغة عربية",
    "أستاذ مساعد لغة عربية",
    "أستاذ مشارك لغة عربية",
    "أستاذ لغة عربية",
]


GULF_LOCATIONS = [
    "Saudi Arabia",
    "United Arab Emirates",
    "Qatar",
    "Kuwait",
    "Bahrain",
    "Oman",
]


def fetch(url, timeout=20):
    """
    Download a webpage.
    """

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            allow_redirects=True,
        )

        if response.status_code != 200:
            return None

        return response.text

    except requests.RequestException:
        return None


def extract_links(html, base_url):
    """
    Extract links from a webpage.
    """

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    results = []

    for link in soup.find_all("a", href=True):

        href = link.get("href")

        if not href:
            continue

        url = urljoin(base_url, href)

        title = link.get_text(" ", strip=True)

        if not title:
            continue

        results.append(
            {
                "title": title,
                "url": url,
            }
        )

    return results


def search_generic_site(search_url, source_name):
    """
    Generic search-page reader.

    This is intentionally simple.
    Individual job sites can later get their own adapters.
    """

    html = fetch(search_url)

    if not html:
        return []

    links = extract_links(html, search_url)

    jobs = []

    for item in links:

        jobs.append(
            {
                "title": item["title"],
                "organization": "",
                "country": "",
                "city": "",
                "source": source_name,
                "job_url": item["url"],
                "application_url": item["url"],
                "posted_date": None,
                "deadline": None,
                "description": "",
            }
        )

    return jobs


def get_sources():
    """
    Return the currently enabled job sources.

    We will add individual source adapters here.
    """

    return [
        {
            "name": "MANUAL_SOURCE",
            "enabled": False,
        }
    ]


def collect_jobs():
    """
    Collect jobs from all enabled sources.
    """

    all_jobs = []

    for source in get_sources():

        if not source.get("enabled"):
            continue

        source_jobs = source.get("function", lambda: [])()

        all_jobs.extend(source_jobs)

    return all_jobs
