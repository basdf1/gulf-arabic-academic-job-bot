from .config import (
    GULF_COUNTRIES,
    ALLOWED_TITLES,
    ARABIC_TERMS,
    EXCLUDED_TERMS,
)


def normalize(text):
    """Normalize text for easier Arabic/English matching."""
    if not text:
        return ""

    text = text.lower()

    # Arabic normalization
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ى": "ي",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(text.split())


def contains_any(text, terms):
    """Return True if any term exists in text."""
    text = normalize(text)

    return any(
        normalize(term) in text
        for term in terms
    )


def is_gulf_country(location):
    """Check whether the job is located in a Gulf country."""
    if not location:
        return False

    return contains_any(location, GULF_COUNTRIES)


def has_allowed_title(title):
    """Check whether the job title matches an allowed academic rank."""
    if not title:
        return False

    return contains_any(title, ALLOWED_TITLES)


def is_arabic_language_job(title, description):
    """
    Check whether the position is specifically related
    to Arabic Language.
    """
    text = f"{title} {description}"

    return contains_any(text, ARABIC_TERMS)


def contains_excluded_term(title, description):
    """
    Reject positions containing one of the excluded
    specialties/roles.
    """
    text = f"{title} {description}"

    return contains_any(text, EXCLUDED_TERMS)


def is_relevant_job(title, description="", location=""):
    """
    Main job filter.

    A job must:
    1. Be in a Gulf country
    2. Have an allowed academic rank
    3. Be related specifically to Arabic Language
    4. Not contain an excluded specialty
    """

    if not is_gulf_country(location):
        return False

    if not has_allowed_title(title):
        return False

    if contains_excluded_term(title, description):
        return False

    if not is_arabic_language_job(title, description):
        return False

    return True
