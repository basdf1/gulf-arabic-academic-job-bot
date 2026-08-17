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
    """Download a page from UAEU."""

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as error:
        print(f"[UAEU] Request failed: {error}")
        return None


def collect_uaeu_jobs():
    """
    Collect jobs from the official UAEU recruitment website.
    """

    print("[UAEU] Collecting jobs...")

    html = fetch_page(JOBS_URL)

    if not html:
        print("[UAEU] Could not access jobs page.")
        return []

    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    for link in soup.find_all("a", href=True):

        title = link.get_text(
            " ",
            strip=True
        )

        href = link.get("href")

        if not title or not href:
            continue

        if "Postings/PostingDetails" not in href:
            continue

        job_url = urljoin(
            BASE_URL,
            href
        )

        jobs.append(
            {
                "title": title,
                "organization": (
                    "United Arab Emirates University"
                ),
                "country": (
                    "United Arab Emirates"
                ),
                "city": "Al Ain",
                "source": "UAEU Official",
                "job_url": job_url,
                "application_url": job_url,
                "posted_date": None,
                "deadline": None,
                "description": "",
            }
        )

    # Remove duplicate URLs
    unique_jobs = {}

    for job in jobs:
        unique_jobs[job["job_url"]] = job

    jobs = list(unique_jobs.values())

    print(
        f"[UAEU] Found {len(jobs)} job postings."
    )

    return jobs
