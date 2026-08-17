import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime


BASE_URL = "https://jobs.uaeu.ac.ae"

SEARCH_URLS = [
    (
        "https://jobs.uaeu.ac.ae/search.jsp"
        "?pager.offset={offset}"
        "&sortBy=postingPostingNo"
        "&sortOrder=asc"
    ),
    (
        "https://jobs.uaeu.ac.ae/search"
        "?pager.offset={offset}"
        "&sortBy=postingPostingNo"
        "&sortOrder=asc"
    ),
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_page(url, timeout=20):
    """
    Download a UAEU page.
    """

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
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
    Extract UAEU posting links from the search results.
    """

    if not html:
        return []

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    links = []

    for anchor in soup.find_all(
        "a",
        href=True,
    ):

        href = anchor["href"].strip()

        if "Postings/PostingDetails" not in href:
            continue

        url = urljoin(
            BASE_URL,
            href,
        )

        if url not in links:
            links.append(url)

    return links


def collect_job_links():
    """
    Collect job links from UAEU's search pages.

    We use pagination instead of scanning thousands
    of random posting IDs.
    """

    all_links = set()

    # UAEU currently has roughly a hundred current vacancies,
    # so three pages of 50 is enough in normal operation.
    offsets = [0, 50, 100, 150]

    for offset in offsets:

        print(
            f"[UAEU] Reading search page "
            f"offset={offset}..."
        )

        html = None

        for template in SEARCH_URLS:

            url = template.format(
                offset=offset
            )

            html = fetch_page(url)

            if html:
                links = extract_job_links(
                    html
                )

                if links:
                    break

        if not html:
            print(
                f"[UAEU] Could not read "
                f"offset={offset}"
            )
            continue

        links = extract_job_links(
            html
        )

        print(
            f"[UAEU] Links found on page: "
            f"{len(links)}"
        )

        if not links:
            # No more pages.
            break

        before = len(all_links)

        all_links.update(links)

        # If this page gave us nothing new,
        # stop pagination.
        if len(all_links) == before:
            break

    return sorted(all_links)


def extract_close_date(text):
    """
    Extract the UAEU close date from a job page.

    Returns:
        YYYY-MM-DD
        or None for Open Until Filled / unknown.
    """

    if not text:
        return None

    normalized = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    # UAEU uses:
    #
    # Close Date
    # 31/08/2026
    #
    # or:
    #
    # Close Date: open until filled

    if re.search(
        r"open\s+until\s+filled",
        normalized,
        re.IGNORECASE,
    ):
        return None

    match = re.search(
        r"Close Date.*?"
        r"(\d{1,2})/(\d{1,2})/(\d{4})",
        normalized,
        re.IGNORECASE,
    )

    if not match:
        return None

    day = int(match.group(1))
    month = int(match.group(2))
    year = int(match.group(3))

    try:
        date_value = datetime(
            year,
            month,
            day,
        )

        return date_value.strftime(
            "%Y-%m-%d"
        )

    except ValueError:
        return None


def parse_job(job_url):
    """
    Download and parse one UAEU job posting.
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

    text = soup.get_text(
        " ",
        strip=True,
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title = ""

    # Try common heading elements first.
    for tag in ["h1", "h2", "h3"]:

        heading = soup.find(tag)

        if heading:

            candidate = heading.get_text(
                " ",
                strip=True,
            )

            if candidate:
                title = candidate
                break

    # Fallback to page title.
    if not title and soup.title:

        title = soup.title.get_text(
            " ",
            strip=True,
        )

    # Remove common website suffix.
    title = re.sub(
        r"\s*\|\s*UAEU.*$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    # --------------------------------------------------------
    # Close date
    # --------------------------------------------------------

    close_date = extract_close_date(
        text
    )

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

        "deadline": close_date,

        "description": text,
    }


def collect_uaeu_jobs():
    """
    Main UAEU collector.

    1. Get current vacancy links.
    2. Open each official posting.
    3. Return structured jobs.
    """

    print(
        "[UAEU] Collecting current jobs..."
    )

    job_links = collect_job_links()

    print(
        f"[UAEU] Total job links found: "
        f"{len(job_links)}"
    )

    jobs = []

    for job_url in job_links:

        job = parse_job(
            job_url
        )

        if job is None:
            continue

        jobs.append(job)

        deadline = (
            job["deadline"]
            if job["deadline"]
            else "Open Until Filled"
        )

        print(
            f"[UAEU] Found: "
            f"{job['title']} | "
            f"Deadline: {deadline}"
        )

    # --------------------------------------------------------
    # Remove duplicate URLs
    # --------------------------------------------------------

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
