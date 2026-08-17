import re


# ============================================================
# TARGET GULF COUNTRIES
# ============================================================

GULF_COUNTRIES = {
    "saudi arabia",
    "kingdom of saudi arabia",
    "saudi",

    "united arab emirates",
    "uae",
    "emirates",

    "qatar",

    "kuwait",

    "bahrain",

    "oman",
    "sultanate of oman",
}


# ============================================================
# TARGET ACADEMIC RANKS
# ============================================================

TARGET_RANKS = [
    "lecturer",

    "assistant professor",
    "assistant professors",

    "associate professor",
    "associate professors",

    "professor",
    "professors",

    "full professor",
    "full professors",
]


# ============================================================
# EXCLUDED JOB TYPES
#
# These are NOT the academic ranks we are looking for.
# ============================================================

EXCLUDED_RANKS = [
    "instructor",
    "language instructor",

    "research assistant",
    "research associate",

    "postdoctoral",
    "postdoctoral fellow",
    "post-doctoral",
    "post doc",
    "postdoc",

    "visiting faculty",

    "teaching assistant",

    "lab specialist",
    "laboratory specialist",
]


# ============================================================
# ARABIC FIELD TERMS
#
# We want Arabic language positions.
# ============================================================

ARABIC_TERMS = [
    "arabic",
    "arabic language",
    "arabic languages",
    "arabic studies",
    "arabic department",
    "department of arabic",
    "arabic faculty",
    "arabic professor",
    "professor of arabic",
    "arabic teaching",
    "arabic education",
    "arabic language education",
    "teaching arabic",
]


# ============================================================
# EXCLUDED SPECIALIZATIONS
#
# User specifically requested these to be removed.
# ============================================================

EXCLUDED_SPECIALIZATIONS = [
    "arabic linguistics",
    "arabic literature",
    "arabic as a foreign language",
    "applied linguistics",
    "language instructor",
]


# ============================================================
# NATIONALITY RESTRICTIONS
#
# A job is rejected ONLY when it explicitly requires
# citizens/nationals of the same country.
# ============================================================

NATIONALITY_RESTRICTIONS = {

    "saudi arabia": [
        "saudi nationals only",
        "saudi national only",
        "saudi citizens only",
        "saudi citizen only",
        "only saudi nationals",
        "only saudi citizens",
        "saudi nationality only",
        "must be a saudi national",
        "must be saudi",
        "للسعوديين فقط",
        "للمواطنين السعوديين فقط",
    ],

    "united arab emirates": [
        "uae nationals only",
        "uae national only",
        "uae citizens only",
        "uae citizen only",
        "emirati nationals only",
        "emirati national only",
        "only uae nationals",
        "only uae citizens",
        "uae nationality only",
        "must be a uae national",
        "must be emirati",
        "للمواطنين الإماراتيين فقط",
        "للمواطنين الاماراتيين فقط",
    ],

    "qatar": [
        "qatari nationals only",
        "qatari national only",
        "qatari citizens only",
        "qatari citizen only",
        "only qatari nationals",
        "only qatari citizens",
        "qatari nationality only",
        "must be a qatari national",
        "must be qatari",
        "للقطريين فقط",
        "للمواطنين القطريين فقط",
    ],

    "kuwait": [
        "kuwaiti nationals only",
        "kuwaiti national only",
        "kuwaiti citizens only",
        "kuwaiti citizen only",
        "only kuwaiti nationals",
        "only kuwaiti citizens",
        "kuwaiti nationality only",
        "must be a kuwaiti national",
        "must be kuwaiti",
        "للكويتيين فقط",
        "للمواطنين الكويتيين فقط",
    ],

    "bahrain": [
        "bahraini nationals only",
        "bahraini national only",
        "bahraini citizens only",
        "bahraini citizen only",
        "only bahraini nationals",
        "only bahraini citizens",
        "bahraini nationality only",
        "must be a bahraini national",
        "must be bahraini",
        "للبحرينيين فقط",
        "للمواطنين البحرينيين فقط",
    ],

    "oman": [
        "omani nationals only",
        "omani national only",
        "omani citizens only",
        "omani citizen only",
        "only omani nationals",
        "only omani citizens",
        "omani nationality only",
        "must be an omani national",
        "must be omani",
        "للعمانيين فقط",
        "للمواطنين العمانيين فقط",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for easier matching.
    """

    if not text:
        return ""

    text = str(text).lower()

    # Replace common separators with spaces.
    text = re.sub(
        r"[/_|]+",
        " ",
        text,
    )

    # Remove repeated whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# COUNTRY CHECK
# ============================================================

def is_gulf_country(country):
    """
    Check whether the country is one of the six Gulf countries.
    """

    country = normalize_text(country)

    if not country:
        return False

    return country in GULF_COUNTRIES


# ============================================================
# COUNTRY NORMALIZATION
# ============================================================

def normalize_country(country):
    """
    Convert country names into a standard form.
    """

    country = normalize_text(country)

    country_map = {

        "saudi": "saudi arabia",
        "kingdom of saudi arabia": "saudi arabia",

        "uae": "united arab emirates",
        "emirates": "united arab emirates",

        "sultanate of oman": "oman",
    }

    return country_map.get(
        country,
        country,
    )


# ============================================================
# ACADEMIC RANK CHECK
# ============================================================

def has_target_rank(title):
    """
    Check whether the job title contains one of the
    requested academic ranks.
    """

    title = normalize_text(title)

    if not title:
        return False

    # Explicitly reject unwanted ranks first.
    for rank in EXCLUDED_RANKS:

        if rank in title:
            return False

    # Then look for requested ranks.
    for rank in TARGET_RANKS:

        if rank in title:
            return True

    return False


# ============================================================
# ARABIC FIELD CHECK
# ============================================================

def is_arabic_field(title, description):
    """
    Determine whether the position is related to Arabic language.
    """

    text = normalize_text(
        f"{title} {description}"
    )

    if not text:
        return False

    # Reject specifically excluded fields first.
    for excluded in EXCLUDED_SPECIALIZATIONS:

        if excluded in text:
            return False

    # Look for Arabic-related terms.
    for term in ARABIC_TERMS:

        if term in text:
            return True

    return False


# ============================================================
# NATIONALITY RESTRICTION CHECK
# ============================================================

def has_nationality_restriction(
    text,
    country,
):
    """
    Return True only when the job explicitly requires
    citizens/nationals of the same country.

    Example:

        Saudi Nationals Only
        -> True

        Open to all nationalities
        -> False

        Experience working with Saudi nationals
        -> False
    """

    text = normalize_text(text)

    if not text:
        return False

    country = normalize_country(country)

    restrictions = NATIONALITY_RESTRICTIONS.get(
        country,
        [],
    )

    for phrase in restrictions:

        if phrase in text:
            return True

    return False


# ============================================================
# MAIN FILTER
# ============================================================

def is_relevant_job(
    title,
    description,
    location,
):
    """
    Main job relevance filter.

    A job must satisfy ALL of the following:

    1. Be in a Gulf country.
    2. Have Lecturer / Assistant Professor /
       Associate Professor / Professor rank.
    3. Be related to Arabic.
    4. Not belong to an excluded specialization.
    5. Not explicitly require citizens of the
       same Gulf country.
    """

    title = normalize_text(title)
    description = normalize_text(description)
    location = normalize_country(location)

    # --------------------------------------------------------
    # 1. Country
    # --------------------------------------------------------

    if not is_gulf_country(location):

        print(
            f"[FILTER] Rejected country: {location}"
        )

        return False

    # --------------------------------------------------------
    # 2. Academic rank
    # --------------------------------------------------------

    if not has_target_rank(title):

        print(
            f"[FILTER] Rejected rank: {title}"
        )

        return False

    # --------------------------------------------------------
    # 3. Arabic field
    # --------------------------------------------------------

    if not is_arabic_field(
        title,
        description,
    ):

        print(
            f"[FILTER] Rejected field: {title}"
        )

        return False

    # --------------------------------------------------------
    # 4. Nationality restriction
    # --------------------------------------------------------

    combined_text = (
        f"{title} {description}"
    )

    if has_nationality_restriction(
        combined_text,
        location,
    ):

        print(
            "[FILTER] Rejected nationality restriction"
        )

        return False

    # --------------------------------------------------------
    # 5. Passed all filters
    # --------------------------------------------------------

    print(
        f"[FILTER] ACCEPTED: {title}"
    )

    return True
