import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://jobs.uaeu.ac.ae"
JOBS_URL = "https://jobs.uaeu.ac.ae/"


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)


def fetch_page(url):
    """Download UAEU jobs page."""

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as error:
        print(f"[UAEU] Request failed: {error}")
        return None


def collect_uaeu_jobs():
    """
    Collect current jobs from UAE University.

    UAEU publishes the job title and closing date
    on its official recruitment portal.
    """

    html = fetch_page(JOBS_URL)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    # Find job posting links.
    for link in soup.find_all("a", href=True):

        title = link.get_text(" ", strip=True)

        href = link.get("href")

        if not title or not href:
            continue

        # UAEU job posting URLs contain Postings/PostingDetails
        if "Postings/PostingDetails" not in href:
            continue

        job_url = urljoin(BASE_URL, href)

        jobs.append(
            {
                "title": title,
                "organization": "United Arab Emirates University",
                "country": "United Arab Emirates",
                "city": "Al Ain",
                "source": "UAEU Official",
                "job_url": job_url,
                "application_url": job_url,
                "posted_date": None,
                "deadline": None,
                "description": "",
            }
        )

    # Remove duplicates
    unique_jobs = {}

    for job in jobs:
        unique_jobs[job["job_url"]] = job

    return list(unique_jobs.values())
