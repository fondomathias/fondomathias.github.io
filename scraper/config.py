"""
Configuration for the EJM/EJME + LinkedIn job scrapers.

This copy is pre-tuned for LABOUR ECONOMICS. Edit this file to change
filters, keywords and paths -- you should not need to touch the two
scraper scripts for ordinary re-targeting.

Both ejm_scraper.py and linkedin_scraper.py do "import config", so this
file MUST sit in the same folder as them and MUST be named config.py.
"""

# ---------------------------------------------------------------- paths ----
# Where the EJM/EJME tracker workbook is written, relative to this folder.
# "uni_list.xlsx" keeps it in this same folder (recommended for a fresh
# setup). "../uni_list.xlsx" writes it one level up.
XLSX_PATH = "uni_list.xlsx"

# Optional econjobmarket.org login. Same folder as this file. Format:
#   EJM_EMAIL=you@example.com
#   EJM_PASSWORD=yourpassword
# If the file is absent the scraper just runs logged out (public feed only,
# which is what almost all of the data comes from anyway).
CREDENTIALS_FILE = "credentials.env"

# ------------------------------------------------------------ geography ----
# Only positions in these countries are kept (exact, case-insensitive match
# on the country string parsed from the ad).
EUROPE = [
    "Albania", "Austria", "Belgium", "Bosnia and Herzegovina", "Bulgaria",
    "Croatia", "Cyprus", "Czech Republic", "Czechia", "Denmark", "Estonia",
    "Finland", "France", "Germany", "Greece", "Hungary", "Iceland",
    "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania",
    "Luxembourg", "Malta", "Moldova", "Montenegro", "Netherlands",
    "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Serbia",
    "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey",
    "Ukraine", "United Kingdom", "UK", "England", "Scotland", "Wales",
    "Northern Ireland",
]
# ADD "United States", "Australia", etc. here if you want a wider net.
COUNTRY_WHITELIST = EUROPE + ["India", "Canada"]

# Cheap lat/lon pre-filter on the EJM feed. Keep these WIDER than
# COUNTRY_WHITELIST: the country string decides in the end.
BOUNDING_BOXES = [
    # (min_lat, max_lat, min_lon, max_lon)
    (34.0, 72.0, -25.0, 45.0),    # Europe
    (6.0, 37.0, 68.0, 98.0),      # India
    (41.0, 84.0, -141.0, -52.0),  # Canada
    # (24.0, 50.0, -125.0, -66.0),  # continental USA -- uncomment if wanted
]

# ------------------------------------------------------- field filtering ----
# EJM category names counting as a direct hit (+10). Case-insensitive
# SUBSTRING match, so "labor" also matches "Labor; Demographic Economics".
PRIMARY_CATEGORIES = ["labor", "labour"]

# Categories counting as a close match (+4).
SECONDARY_CATEGORIES = [
    "demographic", "public economics", "health", "education",
    "development", "any field", "microeconomics", "applied",
]

# Keywords searched in the ad title + body (case-insensitive substring).
# Each hit adds its weight once. This is the main relevance dial.
KEYWORD_WEIGHTS = {
    "labor economics": 6,
    "labour economics": 6,
    "labor market": 5,
    "labour market": 5,
    "employment": 3,
    "unemployment": 4,
    "wage": 4,
    "earnings": 3,
    "inequality": 3,
    "human capital": 4,
    "education economics": 4,
    "economics of education": 4,
    "migration": 3,
    "immigration": 3,
    "personnel economics": 4,
    "family economics": 3,
    "gender": 2,
    "discrimination": 3,
    "search and matching": 4,
    "job search": 3,
    "trade unions": 3,
    "collective bargaining": 3,
    "minimum wage": 4,
    "occupational": 2,
    "skills": 2,
    "automation": 2,
    "applied microeconomics": 4,
    "microeconometrics": 5,
    "causal inference": 4,
    "policy evaluation": 4,
    "difference-in-differences": 4,
    "regression discontinuity": 4,
    "instrumental variable": 3,
    "administrative data": 3,
    "matched employer-employee": 5,
    "register data": 3,
    "panel data": 2,
    "randomized controlled trial": 3,
    "field experiment": 3,
    "economics": 2,
}

# Ads scoring below this are dropped. Score = +10 primary category,
# +4 secondary category, + keyword weights. Raise it if you get noise,
# lower it if you get too few rows.
MIN_SCORE = 3

# Priority labels written to the sheet.
PRIORITY_HIGH = 12    # score >= this  -> "High"
PRIORITY_MEDIUM = 7   # score >= this  -> "Medium", else "Low"

# ------------------------------------------------------- position types ----
# EJM position-type names (lowercase) mapped to the "Type" column.
TYPE_MAP = {
    "assistant professor": "Assistant Professor",
    "postdoctoral scholar": "Postdoc",
    "lecturer": "Lecturer",
    "associate professor": "Associate Professor",
    "full professor": "Full Professor",
    "other academic": "Other academic",
    "other nonacademic": "Non-academic",
    "consultant": "Non-academic",
}
# Only ads whose type is in this list survive (for universities).
KEEP_TYPES = ["Assistant Professor", "Postdoc", "Lecturer"]

# ------------------------------------------------ professor matching -------
# The EJM scraper optionally crawls the hiring department's website and
# ranks faculty profiles by how often these words appear. Used to fill the
# "Prof 1..3" columns (who to address / mention in a cover letter).
PROF_KEYWORDS = [
    "labor economics", "labour economics", "labor market", "labour market",
    "wage", "wages", "earnings", "employment", "unemployment",
    "human capital", "education", "migration", "immigration", "inequality",
    "personnel economics", "family economics", "gender", "discrimination",
    "search and matching", "minimum wage", "trade unions",
    "applied microeconomics", "microeconometrics", "causal inference",
    "policy evaluation", "program evaluation", "field experiment",
    "administrative data", "panel data", "public economics",
]
# Hard caps that keep the prof-matcher polite and fast.
PROF_MAX_FACULTY_PAGES = 2      # faculty-directory pages tried per dept
PROF_MAX_PROFILES = 25          # individual profile pages fetched per dept
PROF_ENABLED = True             # False = never do prof matching

# --------------------------------------------------------------- network ---
REQUEST_DELAY_SECONDS = 1.5     # politeness delay between requests
TIMEOUT = 25                    # per-request timeout in seconds
FEED_TIMEOUT = 180              # reserved for the big EJM JSON feed
FEED_RETRIES = 3                # reserved
PAGE_RETRIES = 2                # reserved
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 EJM-personal-tracker"
)

# ------------------------------------------------------------ EJME source --
# European Job Market for Economists (europeanjobmarketofeconomists.org).
# Its listings are auto-pulled from econjobmarket.org, so every EJME ad maps
# to an EJM position ID. Crawling it (a) tags positions taking part in EJME
# coordination/signalling and (b) admits research institutes / central banks
# that the university-oriented type filter would otherwise drop.
EJME_ENABLED = True
EJME_LISTING_URL = "https://www.europeanjobmarketofeconomists.org/job-listings"
EJME_MAX_PAGES = 40             # pagination safety cap
EJME_MIN_SCORE = 2              # lower bar for EJME-only ads
INCLUDE_PAST_DEADLINES = False  # True = keep ads whose deadline has passed

# Advertiser names containing any of these (case-insensitive substring) are
# treated as research institutes / central banks, which unlocks the extra
# position types below.
RESEARCH_INST_KEYWORDS = [
    "bank", "banca", "banque", "institute", "institut", "research cent",
    "max planck", "cnr", "foundation", "ecb", "bis", "oecd", "cepr",
    "ifo", "diw", "zew", "iza", "bruegel", "cemfi", "eief", "observatory",
    "council", "commission", "agency", "fed ", "fund",
    # labour-relevant additions:
    "ilo", "eurofound", "cedefop", "labour", "labor", "ires", "wifo",
]
RESEARCH_EXTRA_TYPES = ["Other academic", "Non-academic"]

# ------------------------------------- non-European applicant eligibility --
# Ads matching a HARD pattern are EXCLUDED outright (explicit EU/EEA-only
# rules). Ads matching only a SOFT pattern are KEPT but flagged in the
# "Eligibility (non-EU)" column with the matched phrase quoted.
# If you are an EU/EEA citizen and do not care, set both lists to [].
HARD_RESTRICT_PATTERNS = [
    r"must (?:be|hold) (?:a |an )?(?:eu|eea|european union)[\w\s\-]{0,30}(?:citizen|national)",
    r"(?:eu|eea|european union) citizenship is (?:required|mandatory)",
    r"restricted to (?:eu|eea) (?:citizens|nationals)",
    r"only (?:eu|eea) (?:citizens|nationals) (?:are eligible|may apply)",
    r"must be a (?:citizen|national) of an? (?:eu|eea|european union) member state",
    r"applicants must hold citizenship of an? (?:eu|eea|member) state",
]
SOFT_RESTRICT_PATTERNS = [
    r"(?:eu|eea|european union)[\w\s\-]{0,25}(?:citizenship|citizen|national(?:ity)?)",
    r"right to work in [\w\s]{0,25}",
    r"work permit",
    r"eligib\w+ to work in",
    r"security clearance",
    r"visa sponsorship (?:is )?(?:not|un)available",
    r"member state national",
]
