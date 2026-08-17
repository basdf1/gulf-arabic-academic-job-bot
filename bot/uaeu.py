import requests
from bs4 import BeautifulSoup


BASE_URL = "https://jobs.uaeu.ac.ae"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)


# UAEU posting IDs are discovered from the official
# recruitment website/search results.
#
# We start with a range and let the checker decide
# whether each posting is valid and still open.

START_ID = 4000
END_ID = 5300


def fetch_job(job_id):
    """
    Try to retrieve one UAEU job posting.
    """

    url = (
        f"{BASE_URL}/Postings/PostingDetails/"
        f"{job_id}"
    )

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": (
                    "en-US,en;q=0.9,ar;q=0.8"
                ),
            },
            timeout=15,
            allow_redirects=True,
        )

        if response.status_code != 200:
            return None

        html = response.text

        # Make sure this is actually a job page.
        if "Job Description" not in html:
            return None

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        title = soup.title.get_text(
            " ",
            strip=True
        ) if soup.title else ""

        text = soup.get_text(
            " ",
            strip=True
        )

        # Try to get the actual job title.
        heading = soup.find(
            ["h1", "h2", "h3"]
        )

        if heading:
            heading_text = heading.get_text(
                " ",
                strip=True
            )

            if heading_text:
                title = heading_text

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
            "job_url": url,
            "application_url": url,
            "posted_date": None,
            "deadline": None,
            "description": text,
        }

    except requests.RequestException:
        return None


def collect_uaeu_jobs():
    """
    Discover UAEU job postings.

    We scan posting IDs because the main UAEU
    vacancy page loads its content dynamically.
    """

    print("[UAEU] Starting job discovery...")

    jobs = []

    for job_id in range(
        START_ID,
        END_ID + 1
    ):

        job = fetch_job(job_id)

        if job is None:
            continue

        jobs.append(job)

        print(
            f"[UAEU] Found: "
            f"{job['title']} "
            f"({job_id})"
        )

    # Remove duplicate URLs.
    unique_jobs = {}

    for job in jobs:
        unique_jobs[
            job["job_url"]
        ] = job

    jobs = list(
        unique_jobs.values()
    )

    print(
        f"[UAEU] Total discovered: "
        f"{len(jobs)}"
    )

    return jobs
