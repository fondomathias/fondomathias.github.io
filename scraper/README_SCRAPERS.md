# Academic job scrapers: EJM / EJME + LinkedIn

Two Python scripts that build and maintain Excel trackers of academic
economics job openings:

- `ejm_scraper.py` -- econjobmarket.org (EJM) public ads feed, plus the
  European Job Market for Economists (EJME) site. Rich metadata: deadline,
  documents required, number of reference letters, start date, department
  website, and (optionally) the three most topically relevant professors in
  the hiring department.
- `linkedin_scraper.py` -- LinkedIn's logged-out ("guest") job search
  endpoints. Broader and noisier; catches non-academic and portal-only ads
  that never reach EJM.

Both are re-targeted by editing **one** file, `config.py`. The default
config shipped with this bundle is tuned for **labour economics**.

---

## 0. TL;DR

```bash
# one time
python -m venv .venv
.venv\Scripts\activate          # Windows;  source .venv/bin/activate on Mac/Linux
pip install -r requirements.txt

# every time
python ejm_scraper.py --no-profs --dry-run     # see what it would collect
python ejm_scraper.py --no-profs               # write uni_list.xlsx
python linkedin_scraper.py --days 30 --dry-run # first LinkedIn look
python linkedin_scraper.py --days 30           # write linkedin_list.xlsx
```

---

## 1. Files you need

Put all of these in **one folder**. The scripts locate everything relative
to their own location, so the folder can live anywhere.

| File | Required? | What it is |
|---|---|---|
| `ejm_scraper.py` | yes | EJM + EJME scraper |
| `linkedin_scraper.py` | yes | LinkedIn guest scraper |
| `config.py` | **yes** | all filters, keywords, paths. Both scripts do `import config` and crash without it |
| `requirements.txt` | yes | Python dependencies |
| `credentials.env` | no | optional econjobmarket.org login (see 3.4) |

If you received a file called `config_labour_template.py`, **rename it to
`config.py`**. Nothing works until a file named exactly `config.py` sits
next to the two scripts.

Generated automatically on first run (do not create them by hand):

- `uni_list.xlsx` -- the EJM/EJME tracker
- `linkedin_list.xlsx` -- the LinkedIn tracker

---

## 2. Installation

Requires **Python 3.9 or newer** (3.10+ recommended). Check with
`python --version`.

### Windows (PowerShell or CMD)

```
cd path\to\the\folder
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux

```
cd path/to/the/folder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies are `requests`, `beautifulsoup4`, `lxml`, `openpyxl` -- all
pure-install, no compilers, no API keys, no browser drivers.

Quick sanity check (should print nothing and exit cleanly):

```
python -c "import requests, bs4, lxml, openpyxl, config; print('ok')"
```

---

## 3. Re-targeting to your own field

Almost everything lives in `config.py`. Edit it in any text editor; it is
plain Python, so keep the quotes and commas intact.

### 3.1 Fields and keywords (the main dial)

`PRIMARY_CATEGORIES` -- EJM's own category names. A case-insensitive
**substring** match adds **+10** to an ad's score. EJM labels labour ads
"Labor; Demographic Economics", so `"labor"` catches them. Note EJM uses
American spelling; the shipped config lists both `"labor"` and `"labour"`
because LinkedIn ads use either.

`SECONDARY_CATEGORIES` -- adjacent fields, worth **+4**.

`KEYWORD_WEIGHTS` -- a dict of `"phrase": weight` searched in the ad title
and full body text. Every distinct phrase that appears adds its weight
once. This is where you encode what you actually do:

```python
KEYWORD_WEIGHTS = {
    "labor economics": 6,
    "matched employer-employee": 5,
    "minimum wage": 4,
    "difference-in-differences": 4,
    ...
}
```

Rules of thumb:

- All phrases must be **lowercase** (the text is lowercased before matching).
- Matching is plain substring, so `"wage"` also fires inside `"wages"` and
  `"minimum wage"` -- that is usually what you want, but it means very short
  words like `"var"` or `"ols"` will produce false hits. Prefer two-word
  phrases.
- Give 5-6 to phrases that only appear in ads you would genuinely apply to,
  2-3 to supporting methods, 1-2 to generic words.

`MIN_SCORE` -- ads below this are dropped entirely. Start at 3. If the sheet
is full of irrelevant ads, raise it to 5 or 6; if it is nearly empty, drop
to 2 and widen `KEYWORD_WEIGHTS`.

`PRIORITY_HIGH` / `PRIORITY_MEDIUM` -- thresholds for the "Priority" column
(cosmetic; they do not filter anything).

**Calibrate before committing.** Run `python ejm_scraper.py --no-profs
--dry-run`, look at the scores printed for ads you recognise as good, and
set the thresholds from that, not from intuition.

### 3.2 Geography

`COUNTRY_WHITELIST` -- the hard filter. An ad is kept only if the country
parsed from its page matches an entry **exactly** (case-insensitive). To add
the US:

```python
COUNTRY_WHITELIST = EUROPE + ["India", "Canada", "United States"]
```

`BOUNDING_BOXES` -- a cheap lat/lon pre-filter applied to the EJM feed
before any page is fetched. Keep these strictly **wider** than the country
whitelist, otherwise ads are silently dropped before the country check ever
runs. The template has a commented-out USA box; uncomment it if you add the
US to the whitelist.

### 3.3 Position types

`TYPE_MAP` maps EJM's position-type names to the "Type" column, and
`KEEP_TYPES` decides which survive:

```python
KEEP_TYPES = ["Assistant Professor", "Postdoc", "Lecturer"]
```

Add `"Associate Professor"` or `"Full Professor"` if you are past the entry
level. Research institutes and central banks get extra latitude: any
advertiser whose name contains a `RESEARCH_INST_KEYWORDS` substring also
admits the types in `RESEARCH_EXTRA_TYPES` ("Other academic",
"Non-academic"), so ECB/IZA/OECD-style research posts are not thrown away by
the university-oriented filter. Add labour-specific employers (ILO,
Eurofound, Cedefop, national statistical offices) to that list.

### 3.4 Eligibility screening (probably the first thing you will change)

The original author is a non-EU applicant, so both scripts screen ad text
for citizenship restrictions:

- `HARD_RESTRICT_PATTERNS` -- an ad matching one of these regexes is
  **excluded outright** (explicit "EU citizens only" rules).
- `SOFT_RESTRICT_PATTERNS` -- ad is **kept** but the "Eligibility (non-EU)"
  column shows `CHECK: "<the matched phrase>"` for you to read manually.

If you hold EU/EEA citizenship this is pure noise. Disable it with:

```python
HARD_RESTRICT_PATTERNS = []
SOFT_RESTRICT_PATTERNS = []
```

Every row then reads "No restriction found" and nothing is excluded on
eligibility grounds. Conversely, if you need visa sponsorship, keep the soft
list and add phrases you care about.

### 3.5 Professor matching (EJM scraper only)

When enabled, the scraper follows the department website linked on an ad,
looks for a faculty/people/staff page, opens up to `PROF_MAX_PROFILES`
profile pages, and ranks them by how often the words in `PROF_KEYWORDS`
appear. The top three land in the "Prof 1..3" columns -- useful for cover
letters and for judging whether a department is actually a fit.

It is best-effort and by far the slowest part of a run (dozens of extra HTTP
requests per ad, and it fails silently on JavaScript-rendered directories).

- `PROF_KEYWORDS` -- retune to your field alongside `KEYWORD_WEIGHTS`.
- `PROF_ENABLED = False`, or the `--no-profs` flag, turns it off.

Recommended workflow: run with `--no-profs` while you are calibrating, then
one slow full run once the filters are right. On later runs it only re-runs
for rows that are new or still have an empty "Prof 1" cell, so it stays
cheap.

### 3.6 LinkedIn-specific settings

These are **not** in `config.py` -- they sit in a clearly marked block at the
top of `linkedin_scraper.py` (around lines 50-127):

| Constant | Meaning |
|---|---|
| `SEARCH_TERMS` | the search queries. Replace the econometrics wording, e.g. `"assistant professor labor economics"`, `"postdoc labour economics"`, `"research economist labour market"` |
| `LOCATIONS` | one LinkedIn location string per query. Every term is run against every location, so this multiplies runtime |
| `TITLE_HINTS` | a job title must contain one of these before its description is downloaded. Cheap noise filter |
| `TITLE_BONUSES` / `COMPANY_BONUSES` | regex-to-points bonuses on the title and the employer name, added on top of `config.KEYWORD_WEIGHTS` |
| `MIN_SCORE` | LinkedIn's own threshold (default 8, deliberately higher than EJM's) |
| `MAX_PAGES_PER_QUERY` | 25 results per page, default 5 pages |
| `MAX_DETAIL_FETCHES` | cap on description downloads per run (default 150). Anything past the cap is simply picked up next run |
| `DELAY_SECONDS` | politeness delay, 3.0s plus jitter. Do not lower it |

Runtime scales as `len(SEARCH_TERMS) x len(LOCATIONS) x MAX_PAGES_PER_QUERY`
requests at roughly 3.75s each. The defaults (6 terms x 19 locations x 5
pages) are around 570 requests, i.e. **30-40 minutes**. Trim `LOCATIONS` to
the 4-5 countries you would actually move to and it drops to under ten
minutes.

`linkedin_scraper.py` also reads `config.XLSX_PATH` to see which
institutions already appear in the EJM tracker and flags overlaps in the
"In uni_list?" column. If `uni_list.xlsx` does not exist yet, that column is
just left blank -- no error.

---

## 4. Running

### EJM / EJME

```
python ejm_scraper.py                 # full run, both sources, prof matching
python ejm_scraper.py --no-profs      # skip prof matching (much faster)
python ejm_scraper.py --no-ejme       # EJM feed only
python ejm_scraper.py --dry-run       # print what would change, write nothing
```

Flags combine: `--no-profs --dry-run` is the right first command.

What happens, in order: crawl EJME listing pages and map them to EJM
position IDs -> download the EJM public JSON feed (one large request, can
take a minute) -> drop ads outside the bounding boxes, below `MIN_SCORE`, or
of the wrong type -> fetch each surviving ad page for deadline, documents,
letters, department site -> apply the country and eligibility filters ->
optionally match professors -> merge into `uni_list.xlsx`.

Typical wall-clock: 10-20 minutes with `--no-profs`, an hour or more with
prof matching on the first run.

### LinkedIn

```
python linkedin_scraper.py                # postings from the last 7 days
python linkedin_scraper.py --days 30      # wider window -- use this first
python linkedin_scraper.py --max-pages 2  # shallower, faster
python linkedin_scraper.py --dry-run      # preview only
```

Use `--days 30` (or 60) for the first run to backfill, then a weekly
`--days 7`.

No login, no API key, no cookies: only LinkedIn's public logged-out
endpoints are touched, so your own account is never involved and cannot be
flagged. LinkedIn throttles by IP with HTTP 429/999; the script waits 60
seconds, retries once, then skips that URL and keeps whatever it has.

### Scheduling (optional)

- Windows: Task Scheduler -> weekly -> Program `path\to\.venv\Scripts\python.exe`,
  Arguments `ejm_scraper.py --no-profs`, Start in = the folder.
- macOS/Linux cron, Mondays at 08:00:

  ```
  0 8 * * 1 cd /path/to/folder && .venv/bin/python ejm_scraper.py --no-profs
  ```

---

## 5. What you get

### `uni_list.xlsx` (EJM/EJME)

31 columns: EJM ID, Source (EJM / EJME / EJM + EJME), University,
Department, Position Title, Type, Field(s), Priority, Score, Country, City,
Eligibility (non-EU), Deadline, Expected Answer / Interviews, Start Date,
Duration, Degree Required, Documents Required, # LoRs, Application Link,
Dept Website, Prof 1-3 (+ links), Date First Seen, New?, Status, Notes.

Sorted by deadline (undated rows last), header frozen, autofilter on, and
"Status" carries a dropdown: Not started / Drafting / Applied / Interview /
Flyout / Offer / Rejected / Withdrawn.

### `linkedin_list.xlsx`

Job ID, Source, Institution, Position Title, Location, Country, Posted,
Score, Priority, Eligibility (non-EU), Apply Link, In uni_list?, Date First
Seen, New?, Status, Notes. Sorted by score, since LinkedIn ads carry no
deadline.

### How re-runs treat your edits

This is the part worth understanding before you start typing into the sheet.

- Rows are keyed by EJM ID / LinkedIn Job ID, so a re-run **updates** rows
  rather than duplicating them.
- Columns the scraper owns (university, deadline, score, links, ...) are
  **overwritten** with fresh values on every run.
- `Status`, `Notes` and `Date First Seen` are **yours** and are always
  preserved. Put your own tracking there and nowhere else.
- Newly discovered rows are highlighted pale yellow and marked `NEW`; the
  flag clears on the following run.
- A row that disappears from the feed is **kept**, with "No longer listed /
  filtered out" written into empty Notes -- your application history is never
  silently deleted.
- Close the workbook in Excel before running. An open file is locked on
  Windows and the save fails with a `PermissionError`.

---

## 6. Troubleshooting

**`ModuleNotFoundError: No module named 'config'`** -- `config.py` is missing
from the folder, or is named something else. This is the single most common
failure.

**`ModuleNotFoundError: No module named 'bs4'` / `lxml`** -- the virtual
environment is not active, or `pip install -r requirements.txt` was run
against a different Python. Re-activate and reinstall.

**`PermissionError` when saving the xlsx** -- the workbook is open in Excel.
Close it and re-run.

**Feed downloads but zero rows survive** -- almost always the filters. In
order: is your country in `COUNTRY_WHITELIST`, and is it inside a
`BOUNDING_BOXES` rectangle? Is `MIN_SCORE` too high for the keywords you
kept? Do your `PRIMARY_CATEGORIES` strings actually match EJM's category
names? Run with `--dry-run` and read the per-ad log lines: each skip prints
its reason.

**EJME crawl fails** -- the run continues on EJM alone and logs the error;
`--no-ejme` skips it deliberately.

**LinkedIn returns HTTP 429 or 999 repeatedly** -- you are rate-limited.
Wait a few hours, raise `DELAY_SECONDS`, cut `LOCATIONS`, and lower
`MAX_PAGES_PER_QUERY`. Whatever was collected before the throttle is still
written.

**LinkedIn returns 200 but no cards are parsed** -- LinkedIn changed its
markup. The CSS selectors are in `parse_cards()` in `linkedin_scraper.py`
(`h3.base-search-card__title`, `h4.base-search-card__subtitle`,
`.job-search-card__location`). Open one of the search URLs in a browser,
inspect the current class names, and patch. This happens once or twice a
year.

**`TypeError` while sorting the LinkedIn workbook** -- a Score cell was
edited into text. Clear it or put a number back; the Score column is
scraper-owned anyway.

**Everything is excluded on eligibility** -- see 3.4; set both pattern lists
to `[]`.

---

## 7. Etiquette and limits

- Both scripts read only public pages, sleep between requests, and identify
  themselves in the User-Agent. Keep the delays. A personal weekly run is
  well within reasonable use; hammering these sites is not, and gets your IP
  blocked long before it gets you a job.
- The EJM login is optional and only ever used to see ads restricted to
  logged-in users. **Never share `credentials.env`** and never commit it to
  a repository.
- Coverage is not complete. Many positions are advertised only on
  university portals, AEA JOE, or national job boards. Treat these trackers
  as a high-recall first pass, not as the whole market.
- Scores are a triage heuristic, not a judgement of fit. Read the ads.

---

## 8. Suggested first hour

1. Install, then `python -c "import config; print('ok')"`.
2. Open `config.py`. Rewrite `PRIMARY_CATEGORIES`, `SECONDARY_CATEGORIES`
   and `KEYWORD_WEIGHTS` for your own work; set `COUNTRY_WHITELIST`; empty
   the two eligibility pattern lists if they do not apply to you.
3. `python ejm_scraper.py --no-profs --dry-run`. Read the log. Adjust
   `MIN_SCORE` until the ads you would actually apply to sit clearly above
   the ads you would not.
4. `python ejm_scraper.py --no-profs` and open `uni_list.xlsx`.
5. Retune `PROF_KEYWORDS`, then one full `python ejm_scraper.py`.
6. Edit `SEARCH_TERMS` and cut `LOCATIONS` down in
   `linkedin_scraper.py`, then `python linkedin_scraper.py --days 30`.
7. Schedule a weekly run and only ever touch the Status and Notes columns
   by hand.
