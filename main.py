import argparse, sys
# import config, storage, validate
import config, storage, validate, reports


def scrape(keys, debug):
    """Open one headless browser and run each collector in turn."""
    from playwright.sync_api import sync_playwright
    from collectors import REGISTRY
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
            locale="en-US", viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        for k in keys:
            print(f"  collecting {k} ...")
            rows += REGISTRY[k]().collect(page, config.ZIPS, debug)
        browser.close()
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--banks", nargs="*", default=list(config.BANKS), help="subset of bank keys")
    ap.add_argument("--debug", action="store_true", help="save page text + screenshot to debug/")
    a = ap.parse_args()

    df = storage.upsert(scrape(a.banks, a.debug), config.DATA_FILE)

    today = df[df["date"] == df["date"].max()].sort_values("apy", ascending=False)
    print("\nTODAY")
    for _, r in today.iterrows():
        apy = f"{r['apy']:.2f}%" if r["apy"] == r["apy"] else "  -  "
        print(f"  {apy:>7}  {r['bank']} / {r['product']} / {r['zip'] or 'national'}  [{r['status']}]")

    issues = validate.validate(df)
    print("\nISSUES" if issues else "\nNo issues.")
    for i in issues:
        print("  " + i)

    # Fail the run (useful later in GitHub Actions) only if NOTHING worked.
    
    # sys.exit(0 if (today["status"] == "ok").any() else 1)
    reports.build_dashboard(df, config.DASHBOARD)
    print(f"\nDashboard written to {config.DASHBOARD}")
