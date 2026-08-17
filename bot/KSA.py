import re
import requests

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

REQUEST_TIMEOUT = 10
MAX_WORKERS = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


# ------------------------------------------------------------
# SAUDI UNIVERSITY SOURCES
# ------------------------------------------------------------

SOURCES = [
    {
        "name": "King Saud University",
        "country": "Saudi Arabia",
        "city": "Riyadh",
        "url": "https://dfpa.ksu.edu.sa/ar/facultyjobs",
    },
    {
        "name": "Prince Sultan University",
        "country": "Saudi Arabia",
        "city": "Riyadh",
        "url": "https://psu.edu.sa/en/career",
    },
    {
        "name": "Qassim University",
        "country": "Saudi Arabia",
        "city": "Buraidah",
        "url": "https://www.qu.edu.sa/jobs/",
    },
]


# ------------------------------------------------------------
# ACADEMIC FILTER
# ------------------------------------------------------------

ACADEMIC_KEYWORDS = [
    "professor",
    "associate professor",
    "assistant professor",
    "faculty",
    "lecturer",
    "research",
    "researcher",
    "research assistant",
    "postdoctoral",
    "postdoc",
    "academic",
    "أستاذ",
    "أستاذ مشارك",
    "أستاذ مساعد",
    "محاضر",
    "باحث",
    "معيد",
    "هيئة تدريس",
]


def is_academic(title, description=""):

    text = f"{title} {description}".lower()

    return any(
        keyword.lower() in text
        for keyword in ACADEMIC_KEYWORDS
    )


# ------------------------------------------------------------
# DATE PARSER
# ------------------------------------------------------------

def parse_date(text):

    patterns = [
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
        r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        value = match.group(1)

        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d %B %Y",
            "%B %d, %Y",
        ]

        for fmt in formats:

            try:

                return datetime.strptime(
                    value,
                    fmt,
                ).strftime("%Y-%m-%d")

            except ValueError:
                pass

    return None


# ------------------------------------------------------------
# FETCH SOURCE
# ------------------------------------------------------------

def fetch_source(source):

    try:

        response = requests.get(
            source["url"],
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        jobs = []

        # ----------------------------------------------------
        # FIND LINKS / HEADINGS
        # ----------------------------------------------------

        elements = soup.find_all(
            ["a", "h1", "h2", "h3", "h4"]
        )

        for element in elements:

            title = element.get_text(
                " ",
                strip=True,
            )

            if not title:
                continue

            if not is_academic(title):
                continue

            link = element.get("href")

            if link:

                if link.startswith("/"):
                    base = re.match(
                        r"https?://[^/]+",
                        source["url"],
                    )

                    if base:
                        link = (
                            base.group(0)
                            + link
                        )

            else:
                link = source["url"]

            jobs.append({
                "title": title,

                "organization":
                    source["name"],

                "country":
                    source["country"],

                "city":
                    source["city"],

                "source":
                    "Official University",

                "job_url":
                    link,

                "application_url":
                    link,

                "posted_date":
                    None,

                "deadline":
                    parse_date(title),

                "description":
                    title,
            })

        return jobs

    except requests.RequestException:

        return []

    except Exception as error:

        print(
            f"[KSA] Error: {error}",
            flush=True,
        )

        return []


# ------------------------------------------------------------
# COLLECT KSA JOBS
# ------------------------------------------------------------

def collect_ksa_jobs():

    print(
        "[KSA] Collector started",
        flush=True,
    )

    jobs = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [
            executor.submit(
                fetch_source,
                source,
            )
            for source in SOURCES
        ]

        for future in as_completed(futures):

            try:

                found = future.result()

                for job in found:

                    jobs.append(job)

                    deadline = (
                        job["deadline"]
                        if job["deadline"]
                        else "Unknown"
                    )

                    print(
                        f"[KSA] FOUND "
                        f"{job['title']} | "
                        f"Deadline: {deadline}",
                        flush=True,
                    )

            except Exception as error:

                print(
                    f"[KSA] Worker error: "
                    f"{error}",
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
        f"[KSA] Collection finished. "
        f"Jobs found: {len(jobs)}",
        flush=True,
    )

    return jobs
