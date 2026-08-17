# Gulf Arabic Academic Job Bot
# Search criteria

GULF_COUNTRIES = {
    "saudi arabia",
    "united arab emirates",
    "uae",
    "qatar",
    "kuwait",
    "bahrain",
    "oman",
    "السعودية",
    "المملكة العربية السعودية",
    "الإمارات",
    "الإمارات العربية المتحدة",
    "قطر",
    "الكويت",
    "البحرين",
    "عمان",
    "سلطنة عمان",
}

ALLOWED_TITLES = [
    "lecturer",
    "assistant professor",
    "associate professor",
    "professor",
    "faculty member",

    "محاضر",
    "أستاذ مساعد",
    "استاذ مساعد",
    "أستاذ مشارك",
    "استاذ مشارك",
    "أستاذ",
    "استاذ",
    "عضو هيئة تدريس",
]

ARABIC_TERMS = [
    "arabic language",
    "arabic language department",
    "arabic language professor",
    "arabic language lecturer",
    "arabic faculty",
    "لغة عربية",
    "اللغة العربية",
    "قسم اللغة العربية",
]

EXCLUDED_TERMS = [
    "arabic linguistics",
    "arabic literature",
    "arabic as a foreign language",
    "applied linguistics",
    "language instructor",

    "لسانيات",
    "أدب عربي",
    "اللغة العربية لغير الناطقين بها",
    "اللغويات التطبيقية",
    "مدرس لغة",
    "مدرب لغة",
]

CLOSED_TERMS = [
    "closed",
    "expired",
    "position filled",
    "no longer accepting applications",
    "applications are closed",
    "deadline has passed",
    "vacancy closed",

    "انتهى التقديم",
    "التقديم مغلق",
    "انتهت فترة التقديم",
    "الوظيفة مغلقة",
    "تم شغل الوظيفة",
]

OPEN_TERMS = [
    "apply now",
    "apply",
    "submit application",
    "applications are open",
    "how to apply",

    "تقديم",
    "قدم الآن",
    "التقديم مفتوح",
    "طريقة التقديم",
]
