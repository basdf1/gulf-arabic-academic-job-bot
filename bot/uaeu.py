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


def fetch_page(url, timeout=30):
    """
    Download a UAEU page.
    """

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": (
                    "en-US,en;q=0.9,ar;q=0.8"
                ),
            },
            timeout=timeout,
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as error:
        print(
            f"[UAEU] Request failed: {error}"
        )
        return None


def extract_job_links(html):
    """
    Extract UAEU job posting links from HTML.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    links = []

    for link in soup.find_all(
        "a",
        href=True,
    ):

        href = link.get("href")

        if not href:
            continue

        if "Postings/PostingDetails" not in href:
            continue

        job_url = urljoin(
            BASE_URL,
            href,
        )

        if job_url not in links:
            links.append(job_url)

    return links


def fetch_job(job_url):
    """
    Download and parse one UAEU job page.
    """

    html = fetch_page(
        job_url,
        timeout=20,
    )

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # Page title
    page_title = ""

    if soup.title:
        page_title = soup.title.get_text(
            " ",
            strip=True,
        )

    # Main visible text
    description = soup.get_text(
        " ",
        strip=True,
    )

    # Try to find a heading
    heading = soup.find(
        ["h1", "h2", "h3"],
    )

    title = ""

    if heading:
        title = heading.get_text(
            " ",
            strip=True,
        )

    if not title:
        title = page_title

    return {
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
        "description": description,
    }


def collect_uaeu_jobs():
    """
    Collect currently discoverable UAEU jobs.

    We first try the official jobs page instead
    of scanning thousands of posting IDs.
    """

    print(
        "[UAEU] Collecting current jobs..."
    )

    html = fetch_page(
        JOBS_URL,
        timeout=30,
    )

    if not html:
        print(
            "[UAEU] Could not access jobs page."
        )
        return []

    job_links = extract_job_links(
        html
    )

    print(
        f"[UAEU] Job links found: "
        f"{len(job_links)}"
    )

    jobs = []

    for job_url in job_links:

        job = fetch_job(
            job_url
        )

        if job is None:
            continue

        jobs.append(job)

        print(
            f"[UAEU] Found: "
            f"{job['title']}"
        )

    # Remove duplicate URLs
    unique_jobs = {}

    for job in jobs:
        unique_jobs[
            job["job_url"]
        ] = job

    jobs = list(
        unique_jobs.values()
    )

    print(
        f"[UAEU] Total collected: "
        f"{len(jobs)}"
    )

    return jobs
