"""Institutions, products and ZIP codes. Edit here, not in the collectors."""

DATA_FILE = "data/rates.csv"
DEMO_FILE = "data/rates_demo.csv"
DASHBOARD = "docs/index.html"

# ZIP used for banks whose rate depends on location.
# Online banks (Marcus, Amex, Capital One, Wealthfront) are national -> one row, no ZIP.
ZIPS = {
    "WA": ["98005"],   # Kirkland, WA (single ZIP for this project)
}

# scope: "zip" = rate depends on location, "national" = one rate for everyone.
# Every URL is a starting point; verify it still shows the standard (non-promo) rate.
BANKS = {
    "chase":       dict(bank="Chase",       product="Chase Savings",
                        scope="zip",      url="https://www.chase.com/personal/savings/savings-account/interest-rates"),
    "citi":        dict(bank="Citi",        product="Citi Savings",
                        scope="zip",      url="https://www.citi.com/banking/current-interest-rates/savings-accounts"),
    "wells_fargo": dict(bank="Wells Fargo", product="Way2Save Savings",
                        scope="zip",      url="https://www.wellsfargo.com/savings-cds/rates/"),
    "us_bank":     dict(bank="U.S. Bank",   product="Standard Savings",
                        scope="zip",      url="https://www.usbank.com/bank-accounts/savings-accounts.html"),
    "capital_one": dict(bank="Capital One", product="360 Performance Savings",
                        scope="national", url="https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/"),
    "amex":        dict(bank="American Express", product="High Yield Savings",
                        scope="national", url="https://www.americanexpress.com/en-us/banking/online-savings/account/"),
    "wealthfront": dict(bank="Wealthfront", product="Cash Account (base APY)",
                        scope="national", url="https://www.wealthfront.com/cash"),
    "marcus":      dict(bank="Marcus",      product="Online Savings",
                        scope="national", url="https://www.marcus.com/us/en/savings/high-yield-savings"),
}

# Discover savings accounts were folded into Capital One 360 Performance Savings.
# Do NOT scrape Discover separately -> it would double count the same product.
ALIASES = {"discover": "capital_one"}

# Sanity limits used by validate.py
APY_MIN, APY_MAX = 0.0, 6.0
MAX_DAILY_JUMP = 0.50   # percentage points vs previous observation -> flag for review
