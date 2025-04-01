# config.py

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Data paths
RAW_DIR = DATA_DIR / "raw"
SUMMARY_DIR = DATA_DIR / "summarized"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"
METADATA_JSON = DATA_DIR / "eurlex_results.json"
METADATA_JSON_RO = DATA_DIR / "eurlex_ro.json"
PDF_DIR = DATA_DIR / "pdfs"

# OpenAI configuration
OPENAI_API_KEY = ""
OPENAI_MODEL = "gpt-4o-mini"
MAX_SUMMARY_TOKENS = 600
TRUNCATE_WORDS = 5000

# Domain categories
DOMAINS = [
    "Agriculture",
    "Audiovisual and media",
    "Budget",
    "Banking",
    "Competition",
    "Consumers",
    "Culture",
    "Customs",
    "Development",
    "Digital single market",
    "Economic and monetary affairs",
    "Education, training, youth, sport",
    "Employment and social policy",
    "Energy",
    "Enlargement",
    "Enterprise",
    "Environment and climate change",
    "External relations",
    "External trade",
    "Food safety",
    "Foreign and security policy",
    "Fraud and corruption",
    "Humanitarian Aid and Civil Protection",
    "Human rights",
    "Institutional affairs",
    "Internal market",
    "Justice, freedom and security",
    "Oceans and fisheries",
    "Public health",
    "Regional policy",
    "Research and innovation",
    "Taxation",
    "Transport",
    "Others/Unidentified",
]

# EUR-Lex scraping configuration
BASE_URL = "https://eur-lex.europa.eu/"
DEFAULT_TARGET_YEAR = 2025

CATEGORY_QUERY_PARAMS = {
    "regulation": "DB_TYPE_OF_ACT=regulation&typeOfActStatus=REGULATION",
    "directive": "DB_TYPE_OF_ACT=directive&typeOfActStatus=DIRECTIVE",
    "decision": "DB_TYPE_OF_ACT=decision&typeOfActStatus=DECISION",
    "com_join": "DB_TYPE_OF_ACT=comJoin&typeOfActStatus=COM_JOIN",
    "sec_swd": "DB_TYPE_OF_ACT=secSwd&typeOfActStatus=SEC_SWD",
}

BASE_QUERY_STRING = (
    "wh0=andCOMPOSE%3DENG%2CorEMBEDDED_MANIFESTATION-TYPE%3Dpdf%3BEMBEDDED_MANIFESTATION-TYPE%3Dpdfa1a"
    "%3BEMBEDDED_MANIFESTATION-TYPE%3Dpdfa1b%3BEMBEDDED_MANIFESTATION-TYPE%3Dpdfa2a%3BEMBEDDED_MANIFESTATION-TYPE"
    "%3Dpdfx%3BEMBEDDED_MANIFESTATION-TYPE%3Dpdf1x%3BEMBEDDED_MANIFESTATION-TYPE%3Dhtml%3BEMBEDDED_MANIFESTATION-TYPE"
    "%3Dxhtml%3BEMBEDDED_MANIFESTATION-TYPE%3Ddoc%3BEMBEDDED_MANIFESTATION-TYPE%3Ddocx&lang=en&SUBDOM_INIT=ALL_ALL"
    "&DTS_DOM=ALL&type=advanced&DTS_SUBDOM=ALL_ALL&qid=1742290840805"
)

BASE_URL_RO = "https://eur-lex.europa.eu/search.html?SUBDOM_INIT=MNE&DB_AUTHOR=ROU&DTS_SUBDOM=MNE&DTS_DOM=NATIONAL_LAW&lang=en&type=advanced&qid=1743177753381"


def build_query_url(target_year: int, page: int, category: str) -> str:
    if category not in CATEGORY_QUERY_PARAMS:
        raise ValueError(
            f"Invalid category. Choose from: {', '.join(CATEGORY_QUERY_PARAMS.keys())}"
        )

    start_date = f"0101{target_year}"
    end_date = f"3112{target_year}"
    date_segment = (
        f"&date0=ALL%3A{start_date}%7C{end_date}&sortOne=DD&sortOneOrder=desc"
    )

    category_segment = CATEGORY_QUERY_PARAMS[category]

    return f"{BASE_URL}search.html?{BASE_QUERY_STRING}&{category_segment}{date_segment}&page={page}"
