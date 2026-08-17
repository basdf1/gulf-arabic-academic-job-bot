import re
import requests
from bs4 import BeautifulSoup

from .config import CLOSED_TERMS, OPEN_TERMS


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)


def fetch_page(url, timeout=20):
    """
    Download a job/application page.
    Returns HTML or None if the page cannot be accessed.
    """

    if not url:
        return None

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            allow_redirects=True,
        )

        if response.status_code != 200:
            return None

        return response.text

    except requests.RequestException:
        return None


def clean_text(html):
    """Convert HTML into readable text."""

    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts/styles
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    return " ".join(soup.stripped_strings).lower()


def find_deadline(text):
    """
    Try to find common deadline formats.
    This is only a first-stage detector.
    """

    patterns = [
        r"deadline[:\s-]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
        r"closing date[:\s-]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
        r"application deadline[:\s-]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1)

    return None


def has_apply_button(soup):
    """
    Look for links/buttons that appear to lead to an application.
    """

    apply_words = [
        "apply",
        "apply now",
        "submit application",
        "application",
        "تقديم",
        "قدم الآن",
        "التقديم",
    ]

    for element in soup.find_all(["a", "button", "input"]):

        text = element.get_text(" ", strip=True).lower()

        value = element.get("value", "")
        value = str(value).lower()

        combined = f"{text} {value}"

        if any(word in combined for word in apply_words):
            return True

    return False


def check_application_status(url):
    """
    Determine whether an application appears to be open.

    Returns:
        OPEN
        CLOSED
        UNKNOWN
    """

    html = fetch_page(url)

    if not html:
        return "UNKNOWN"

    soup = BeautifulSoup(html, "html.parser")

    text = clean_text(html)

    # Closed status always has priority.
    for term in CLOSED_TERMS:

        if term.lower() in text:
            return "CLOSED"

    # Look for an application button/link.
    if has_apply_button(soup):

        # We found an application mechanism.
        return "OPEN"

    # Look for explicit open wording.
    for term in OPEN_TERMS:

        if term.lower() in text:
            return "OPEN"

    return "UNKNOWN"


def verify_job_application(url):
    """
    Public function used by the bot.
    """

    status = check_application_status(url)

    return {
        "status": status,
        "url": url,
    }
