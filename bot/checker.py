import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from urllib.parse import urljoin


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)


# كلمات تعني أن التقديم مغلق
CLOSED_TERMS = [
    "closed",
    "expired",
    "position filled",
    "filled",
    "no longer accepting applications",
    "applications are closed",
    "application closed",
    "deadline has passed",
    "vacancy closed",

    "انتهى التقديم",
    "التقديم مغلق",
    "انتهت فترة التقديم",
    "الوظيفة مغلقة",
    "تم شغل الوظيفة",
]


# كلمات تعني أن الوظيفة مفتوحة
OPEN_TERMS = [
    "apply now",
    "apply",
    "submit application",
    "applications are open",
    "how to apply",
    "open until filled",
    "open until filled.",

    "تقديم",
    "قدم الآن",
    "التقديم مفتوح",
    "طريقة التقديم",
]


# أسماء الأشهر الإنجليزية
MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def fetch_page(url, timeout=30):
    """
    Download the job/application page.
    """

    if not url:
        return None

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            },
            timeout=timeout,
            allow_redirects=True,
        )

        if response.status_code != 200:
            print(
                f"[CHECKER] HTTP {response.status_code}: {url}"
            )
            return None

        return response.text

    except requests.RequestException as error:
        print(f"[CHECKER] Request failed: {error}")
        return None


def clean_text(html):
    """
    Convert HTML into readable lowercase text.
    """

    soup = BeautifulSoup(html, "html.parser")

    for element in soup(
        ["script", "style", "noscript", "svg"]
    ):
        element.decompose()

    return " ".join(
        soup.stripped_strings
    ).lower()


def find_apply_link(html, base_url):
    """
    Find a likely application link.
    """

    soup = BeautifulSoup(html, "html.parser")

    apply_words = [
        "apply",
        "apply now",
        "submit application",
        "application",
        "تقديم",
        "قدم الآن",
        "التقديم",
    ]

    for element in soup.find_all("a", href=True):

        text = element.get_text(
            " ",
            strip=True
        ).lower()

        href = element.get("href")

        if not href:
            continue

        combined = f"{text} {href.lower()}"

        if any(
            word in combined
            for word in apply_words
        ):
            return urljoin(
                base_url,
                href
            )

    return None


def extract_close_date(text):
    """
    Try to find a closing/deadline date.

    Returns:
        datetime.date
        or None
    """

    # Example:
    # Close Date: 30/09/2026
    numeric_patterns = [
        r"close date\s*[:\-]?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
        r"closing date\s*[:\-]?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
        r"deadline\s*[:\-]?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
        r"application deadline\s*[:\-]?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
    ]

    for pattern in numeric_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))

            try:
                return date(
                    year,
                    month,
                    day
                )
            except ValueError:
                pass

    # Example:
    # Close Date: September 30, 2026
    month_names = "|".join(
        MONTHS.keys()
    )

    month_pattern = (
        rf"(?:close date|closing date|deadline|"
        rf"application deadline)"
        rf"\s*[:\-]?\s*"
        rf"({month_names})\s+"
        rf"(\d{{1,2}}),?\s+"
        rf"(\d{{4}})"
    )

    match = re.search(
        month_pattern,
        text,
        re.IGNORECASE
    )

    if match:

        month_name = (
            match.group(1).lower()
        )

        month = MONTHS.get(
            month_name
        )

        day = int(match.group(2))
        year = int(match.group(3))

        try:
            return date(
                year,
                month,
                day
            )
        except ValueError:
            pass

    return None


def check_explicit_status(text):
    """
    Check explicit OPEN/CLOSED wording.
    """

    # Closed always has priority.
    for term in CLOSED_TERMS:

        if term in text:
            return "CLOSED"

    for term in OPEN_TERMS:

        if term in text:
            return "OPEN"

    return "UNKNOWN"


def check_application_status(url):
    """
    Main application-status checker.

    Rules:

    1. Explicit closed status -> CLOSED
    2. Past deadline -> CLOSED
    3. Future deadline -> OPEN
    4. Open-until-filled -> OPEN
    5. Working Apply button -> OPEN
    6. Otherwise -> UNKNOWN
    """

    html = fetch_page(url)

    if not html:
        return {
            "status": "UNKNOWN",
            "deadline": None,
            "application_url": None,
            "reason": "Page could not be accessed",
        }

    text = clean_text(html)

    # --------------------------------
    # 1. Explicit status
    # --------------------------------

    explicit_status = check_explicit_status(
        text
    )

    if explicit_status == "CLOSED":
        return {
            "status": "CLOSED",
            "deadline": None,
            "application_url": None,
            "reason": "Page contains a closed-status message",
        }

    # --------------------------------
    # 2. Deadline
    # --------------------------------

    deadline = extract_close_date(
        text
    )

    today = datetime.now().date()

    if deadline:

        if deadline < today:

            return {
                "status": "CLOSED",
                "deadline": deadline.isoformat(),
                "application_url": None,
                "reason": "Deadline has passed",
            }

        return {
            "status": "OPEN",
            "deadline": deadline.isoformat(),
            "application_url": find_apply_link(
                html,
                url
            ),
            "reason": "Deadline has not passed",
        }

    # --------------------------------
    # 3. Open Until Filled
    # --------------------------------

    if "open until filled" in text:

        return {
            "status": "OPEN",
            "deadline": None,
            "application_url": find_apply_link(
                html,
                url
            ),
            "reason": "Open until filled",
        }

    # --------------------------------
    # 4. Application link/button
    # --------------------------------

    application_url = find_apply_link(
        html,
        url
    )

    if application_url:

        return {
            "status": "OPEN",
            "deadline": None,
            "application_url": application_url,
            "reason": "Application link found",
        }

    # --------------------------------
    # 5. Cannot confirm
    # --------------------------------

    return {
        "status": "UNKNOWN",
        "deadline": None,
        "application_url": None,
        "reason": "Could not confirm application status",
    }


def verify_job_application(url):
    """
    Public function used by main.py.
    """

    result = check_application_status(
        url
    )

    return result
