import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


BASE_URL = "https://jobs.uaeu.ac.ae"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_job(job_id):
    """
    Fetch one UAEU job posting.
    """

    url = (
        f"{BASE_URL}/Postings/PostingDetails/"
        f"{job_id}"
    )

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10,
        )

        if response.status_code != 200:
            return None

        html = response.text

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        text = soup.get_text(
            " ",
            strip=True,
        )

        if "Job Description" not in text:
            return None

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = ""

        for tag in ["h1", "h2", "h3"]:

            heading = soup.find(tag)

            if heading:

                title = heading.get_text(
                    " ",
                    strip=True,
                )

                if title:
                    break

        if not title and soup.title:

            title = soup.title.get_text(
                " ",
                strip=True,
            )

        # ----------------------------------------------------
        # CLOSE DATE
        # ----------------------------------------------------

        deadline = None

        match = re.search(
            r"Close Date.*?"
            r"(\d{1,2}/\d{1,2}/\d{4})",
            text,
            re.IGNORECASE,
        )

        if match:

            try:

                deadline = datetime.strptime(
                    match.group(1),
                    "%d/%m/%Y",
                ).strftime(
                    "%Y-%m-%d"
                )

            except ValueError:
                deadline = None

        return {
            "title": title,

            "organization":
                "United Arab Emirates University",

            "country":
                "United Arab Emirates",

            "city":
                "Al Ain",

            "source":
                "UAEU Official",

            "job_url":
                url,

            "application_url":
                url,

            "posted_date":
                None,

            "deadline":
                deadline,

            "description":
                text,
        }

    except requests.RequestException:
        return None


def collect_uaeu_jobs():
    """
    Collect recent UAEU postings.

    We use a limited recent ID window instead of
    scanning thousands of old postings.
    """

    print(
        "[UAEU] Collecting recent postings..."
    )

    jobs = []

    # Current UAEU postings are around this range.
    # Keep the range limited so GitHub Actions stays fast.
    start_id = 5000
    end_id = 5300

    for job_id in range(
        start_id,
        end_id + 1,
    ):

        job = fetch_job(
            job_id
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
            f"{job['title']} "
            f"({job_id}) | "
            f"Deadline: {deadline}"
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
