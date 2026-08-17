import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

REQUEST_TIMEOUT = 10
MAX_WORKERS = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


# ------------------------------------------------------------
# OFFICIAL SAUDI SOURCES
# ------------------------------------------------------------

SOURCES = [
    {
        "name": "Prince Sultan University",
        "city": "Riyadh",
        "url": "https://psu.edu.sa/en/career",
        "type": "career",
    },
    {
        "name": "Qassim University",
        "city": "Buraidah",
        "url": "https://www.qu.edu.sa/jobs/",
        "type": "news",
    },
]


# ------------------------------------------------------------
# ACADEMIC KEYWORDS
# ------------------------------------------------------------

ACADEMIC_KEYWORDS = [
    "professor",
    "assistant professor",
    "associate professor",
    "full professor",
    "faculty",
    "lecturer",
    "instructor",
    "research",
    "researcher",
    "research assistant",
    "postdoctoral",
    "postdoc",
    "academic",

    "أستاذ",
    "أستاذ مشارك",
    "أستاذ مساعد",
    "أستاذ متفرغ",
    "محاضر",
    "مدرس",
    "معيد",
    "باحث",
    "باحث مساعد",
    "باحث ما بعد الدكتوراه",
    "وظائف أكاديمية",
    "وظائف أكاديمية",
    "هيئة التدريس",
]


# ------------------------------------------------------------
# DATE PARSER
# ------------------------------------------------------------

MONTHS_AR = {
    "يناير": 1,
    "فبراير": 2,
    "مارس": 3,
    "أبريل": 4,
    "ابريل": 4,
    "مايو": 5,
    "يونيو": 6,
    "يوليو": 7,
    "أغسطس": 8,
    "اغسطس": 8,
    "سبتمبر": 9,
    "أكتوبر": 10,
    "اكتوبر": 10,
    "نوفمبر": 11,
    "ديسمبر": 12,
}


def parse_date(text):

    if not text:
        return None

    # English / numeric dates
    patterns = [
        (
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
            ["%d/%m/%Y", "%d-%m-%Y"],
        ),
        (
            r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
            ["%B %d, %Y"],
        ),
        (
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            ["%d %B %Y"],
        ),
    ]

    for pattern, formats in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        value = match.group(1)

        for fmt in formats:

            try:
                return datetime.strptime(
                    value,
                    fmt,
                ).strftime("%Y-%m-%d")

            except ValueError:
                pass

    # Arabic month dates
    arabic_pattern = (
        r"(\d{1,2})\s+("
        + "|".join(MONTHS_AR.keys())
        + r")\s+(\d{4})"
    )

    match = re.search(
        arabic_pattern,
        text,
        flags=re.IGNORECASE,
    )

    if match:

        day = int(match.group(1))
        month = MONTHS_AR[match.group(2)]
        year = int(match.group(3))

        try:

            return datetime(
                year,
                month,
                day,
            ).strftime("%Y-%m-%d")

        except ValueError:
            pass

    return None


# ------------------------------------------------------------
# ACADEMIC CHECK
# ------------------------------------------------------------

def is_academic(title, description=""):

    text = (
        f"{title} {description}"
    ).lower()

    return any(
        keyword.lower() in text
        for keyword in ACADEMIC_KEYWORDS
    )


# ------------------------------------------------------------
# NORMALIZE TITLE
# ------------------------------------------------------------

def clean_title(title):

    title = re.sub(
        r"\s+",
        " ",
        title,
    ).strip()

    title = re.sub(
        r"^\s*[-–—:|]\s*",
        "",
        title,
    )

    return title


# ------------------------------------------------------------
# FETCH PAGE
# ------------------------------------------------------------

def fetch_page(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            print(
                f"[KSA] HTTP {response.status_code}: {url}",
                flush=True,
            )
            return None

        if not response.text:
            return None

        return BeautifulSoup(
            response.text,
            "html.parser",
        )

    except requests.RequestException as error:

        print(
            f"[KSA] Request error: {error}",
            flush=True,
        )

        return None


# ------------------------------------------------------------
# PRINCE SULTAN UNIVERSITY
# ------------------------------------------------------------

def collect_psu(source):

    soup = fetch_page(
        source["url"]
    )

    if not soup:
        return []

    jobs = []

    # PSU career page contains individual career links.
    for link in soup.find_all("a", href=True):

        title = link.get_text(
            " ",
            strip=True,
        )

        href = link.get("href")

        if not title or not href:
            continue

        title = clean_title(title)

        if not is_academic(title):
            continue

        job_url = urljoin(
            source["url"],
            href,
        )

        # Avoid navigation / repeated links
        if "/career/" not in job_url:
            continue

        # Fetch individual job page
        job_soup = fetch_page(
            job_url
        )

        description = ""
        deadline = None
        posted_date = None

        if job_soup:

            page_text = job_soup.get_text(
                " ",
                strip=True,
            )

            description = page_text

            # Application Due
            due_match = re.search(
                r"Application Due\s*:?\s*"
                r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
                page_text,
                flags=re.IGNORECASE,
            )

            if due_match:
                deadline = parse_date(
                    due_match.group(1)
                )

            # Posted
            posted_match = re.search(
                r"Posted\s*:?\s*"
                r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
                page_text,
                flags=re.IGNORECASE,
            )

            if posted_match:
                posted_date = parse_date(
                    posted_match.group(1)
                )

            # Better title
            heading = job_soup.find(
                ["h1", "h2"]
            )

            if heading:

                heading_text = heading.get_text(
                    " ",
                    strip=True,
                )

                if heading_text:
                    title = clean_title(
                        heading_text
                    )

        if not is_academic(
            title,
            description,
        ):
            continue

        jobs.append({
            "title": title,
            "organization": source["name"],
            "country": "Saudi Arabia",
            "city": source["city"],
            "source": "Official University",
            "job_url": job_url,
            "application_url": job_url,
            "posted_date": posted_date,
            "deadline": deadline,
            "description": description,
        })

    return jobs


# ------------------------------------------------------------
# QASSIM UNIVERSITY
# ------------------------------------------------------------

def collect_qassim(source):

    soup = fetch_page(
        source["url"]
    )

    if not soup:
        return []

    jobs = []

    # The Qassim jobs page is an announcement archive.
    for link in soup.find_all(
        "a",
        href=True,
    ):

        title = link.get_text(
            " ",
            strip=True,
        )

        href = link.get("href")

        if not title or not href:
            continue

        title = clean_title(title)

        if not is_academic(title):
            continue

        job_url = urljoin(
            source["url"],
            href,
        )

        # Fetch announcement
        job_soup = fetch_page(
            job_url
        )

        description = title
        deadline = None
        posted_date = None

        if job_soup:

            description = job_soup.get_text(
                " ",
                strip=True,
            )

            posted_date = parse_date(
                description
            )

            deadline = parse_date(
                description
            )

        jobs.append({
            "title": title,
            "organization": source["name"],
            "country": "Saudi Arabia",
            "city": source["city"],
            "source": "Official University",
            "job_url": job_url,
            "application_url": job_url,
            "posted_date": posted_date,
            "deadline": deadline,
            "description": description,
        })

    return jobs


# ------------------------------------------------------------
# COLLECT ONE SOURCE
# ------------------------------------------------------------

def collect_source(source):

    if source["type"] == "career":
        return collect_psu(source)

    if source["type"] == "news":
        return collect_qassim(source)

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

        futures = {
            executor.submit(
                collect_source,
                source,
            ): source
            for source in SOURCES
        }

        for future in as_completed(
            futures
        ):

            source = futures[future]

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
                        f"{job['organization']} | "
                        f"Deadline: {deadline}",
                        flush=True,
                    )

            except Exception as error:

                print(
                    f"[KSA] Worker error "
                    f"{source['name']}: "
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
