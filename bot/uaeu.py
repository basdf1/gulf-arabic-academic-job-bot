import re
import requests

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


BASE_URL = "https://jobs.uaeu.ac.ae"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

START_ID = 5000
END_ID = 5300

REQUEST_TIMEOUT = 5
MAX_WORKERS = 20


# ------------------------------------------------------------
# FETCH ONE JOB
# ------------------------------------------------------------

def fetch_job(job_id):

    url = (
        f"{BASE_URL}/Postings/PostingDetails/"
        f"{job_id}"
    )

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )

        if response.status_code != 200:
            return None

        html = response.text

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

        # Not a real posting
        if "Job Description" not in text:
            return None

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = ""

        for tag in ("h1", "h2", "h3"):

            heading = soup.find(tag)

            if heading:

                candidate = heading.get_text(
                    " ",
                    strip=True,
                )

                if candidate:

                    title = candidate

                    break

        if not title and soup.title:

            title = soup.title.get_text(
                " ",
                strip=True,
            )

        # Clean title
        title = re.sub(
            r"\s*\|\s*UAEU.*$",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()

        # ----------------------------------------------------
        # CLOSE DATE
        # ----------------------------------------------------

        deadline = None

        date_match = re.search(
            r"Close\s*Date.*?"
            r"(\d{1,2}/\d{1,2}/\d{4})",
            text,
            flags=re.IGNORECASE,
        )

        if date_match:

            try:

                deadline = datetime.strptime(
                    date_match.group(1),
                    "%d/%m/%Y",
                ).strftime(
                    "%Y-%m-%d"
                )

            except ValueError:

                deadline = None

        # ----------------------------------------------------
        # OPEN UNTIL FILLED
        # ----------------------------------------------------

        if re.search(
            r"open\s+until\s+filled",
            text,
            flags=re.IGNORECASE,
        ):

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

    except Exception as error:

        print(
            f"[UAEU] Error on {job_id}: {error}",
            flush=True,
        )

        return None


# ------------------------------------------------------------
# COLLECT JOBS
# ------------------------------------------------------------

def collect_uaeu_jobs():

    print(
        "[UAEU] Collector started",
        flush=True,
    )

    print(
        f"[UAEU] Checking IDs "
        f"{START_ID}-{END_ID}",
        flush=True,
    )

    job_ids = range(
        START_ID,
        END_ID + 1,
    )

    jobs = []

    completed = 0

    # --------------------------------------------------------
    # PARALLEL REQUESTS
    # --------------------------------------------------------

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = {
            executor.submit(
                fetch_job,
                job_id,
            ): job_id
            for job_id in job_ids
        }

        for future in as_completed(
            futures
        ):

            completed += 1

            job_id = futures[future]

            try:

                job = future.result()

            except Exception as error:

                print(
                    f"[UAEU] Worker error "
                    f"{job_id}: {error}",
                    flush=True,
                )

                job = None

            if job:

                jobs.append(job)

                deadline = (
                    job["deadline"]
                    if job["deadline"]
                    else "Open Until Filled"
                )

                print(
                    f"[UAEU] FOUND "
                    f"{job['title']} "
                    f"({job_id}) | "
                    f"Deadline: {deadline}",
                    flush=True,
                )

            # Progress every 25 requests
            if completed % 25 == 0:

                print(
                    f"[UAEU] Progress: "
                    f"{completed}/"
                    f"{END_ID - START_ID + 1}",
                    flush=True,
                )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
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
        f"[UAEU] Collection finished. "
        f"Jobs found: {len(jobs)}",
        flush=True,
    )

    return jobs
