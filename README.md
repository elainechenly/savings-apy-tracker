# Savings APY Tracker

Tracks the **standard (non-promo) savings APY** of nine US banks/institutes every day, stores the history in a CSV file, and publishes a dashboard with today's rates and the historical trend.

**Live dashboard:** [https://elainechenly.github.io/savings-apy-tracker/](https://elainechenly.github.io/savings-apy-tracker/)

> This is a personal project. It reports publicly advertised rates, is not financial advice, and has no affiliation with any bank. Always confirm a rate on the bank's own site before acting on it.

## What is tracked

Only the rate a **regular customer** gets. Promotional, new-customer, referral, relationship and boost rates are excluded and, where useful, mentioned in the CSV `note` column.

| Bank | Product tracked | Rate depends on location? | Not counted |
|---|---|---|---|
| Chase | Chase Savings | Yes (ZIP) | Premier Savings |
| Citi | Citi Savings, Everyday Benefits tier | Page shows no ZIP field | Priority, Citigold and Private Client boost rates |
| Wells Fargo | Way2Save Savings | Yes (ZIP) | Platinum Savings, 3.25% new-customer promo |
| U.S. Bank | Bank Smartly Savings, standard rate | Yes (ZIP) | 1.00%-3.50% relationship rates (need a checking account) |
| Capital One | 360 Performance Savings | No | n/a |
| American Express | High Yield Savings | No | CDs |
| Marcus | Online Savings | No | Referral boost |
| Wealthfront | Cash Account, base APY | No | New-client boost |

Location-based banks are checked for ZIP **98005** (Bellevue, WA). Change it in `config.py`.

## How it works

1. `main.py` opens each bank's rate page in a headless browser (Playwright), enters the ZIP where needed, and reads the page text.
2. Each bank has a small collector in `collectors/` with an exact pattern (`primary`) that matches only the standard rate. If the page shows something unexpected, the program records **why** instead of guessing.
3. `storage.py` writes one row per bank per day to `data/rates.csv`. Re-running on the same day replaces that day's rows.
4. `validate.py` flags problems: a bank that failed, a bank with no row, an APY outside 0-6%, or a day-over-day jump above 0.5 points.
5. `reports.py` fills `template.html` with the CSV data and writes `docs/index.html`.
6. A GitHub Actions workflow runs all of this daily and publishes the dashboard to GitHub Pages.

### Status values in the CSV

| Status | Meaning |
|---|---|
| `ok` | Rate read successfully |
| `ambiguous` | The patterns found different numbers; nothing recorded |
| `pattern_missing` | The page loaded but the pattern did not match (layout changed?) |
| `not_found` / `only_promo` | No usable standard rate found on the page |
| `error` | Timeout, bot block or network problem |
| `needs_calibration` | Collector marked as not yet verified (never records an APY) |

### CSV columns

`date, fetched_at, bank, product, state, zip, apy, rate_type, status, source_url, note`

## Project layout

```
config.py            banks, URLs, ZIP code, validation limits
main.py              runs everything
collectors/
  base.py            shared scraping logic
  browser.py         ZIP entry, clicks, waits, missing-page detection
  chase.py, citi.py, wells_fargo.py, us_bank.py        location-based banks
  capital_one.py, amex.py, marcus.py, wealthfront.py   national banks
storage.py           reads/writes data/rates.csv
validate.py          data quality checks
reports.py           builds the dashboard
template.html        dashboard page
data/rates.csv       the history
.github/workflows/daily.yml   daily run + GitHub Pages deploy
```

## Run it yourself

```bash
pip install -r requirements.txt
playwright install chromium
python main.py                              # all banks
python main.py --banks marcus amex          # only some banks
python main.py --debug                      # also save page text + screenshots to debug/
```

Results go to `data/rates.csv`, and the dashboard to `docs/index.html`.

## Daily automation

`.github/workflows/daily.yml` runs every day at **16:37 UTC** (9:37 AM Pacific in summer, 8:37 AM in winter) and can also be started by hand from the Actions tab (**Run workflow**).

- **collect job:** installs dependencies, runs `python main.py --debug`, commits the updated `data/rates.csv`, and packages the dashboard. The job fails only if **every** bank fails.
- **deploy job:** publishes the dashboard to GitHub Pages.
- Page text and screenshots of each run are kept for 7 days as the `debug` artifact.
- GitHub may delay scheduled runs, and it can disable scheduled workflows in a public repo after 60 days without activity. If the workflow ever shows as disabled, click **Enable workflow** in the Actions tab.

## Maintenance

- **A bank shows `pattern_missing` or `not_found`:** download the `debug` artifact from the latest run, look at that bank's `.txt` and `.png`, and update its `primary` pattern in `collectors/<bank>.py`.
- **Add a bank:** add an entry to `BANKS` in `config.py`, create `collectors/<name>.py` (set `calibrated = False` while testing), register it in `collectors/__init__.py`, then run `python main.py --banks <name> --debug`.
- **Change the ZIP:** edit `ZIPS` in `config.py`.

## Known limitations

- Scraping is fragile: banks redesign pages and some block automated visitors, especially from cloud servers. The program is built to report failures clearly, not to hide them.
- Citi's rate page has no ZIP field, so the ZIP cannot be confirmed for Citi.
- Rates on bank pages change during the day; each row reflects the moment it was fetched (`fetched_at`).
- Check each bank's terms of use before running automated checks, and keep the schedule gentle (once a day).
