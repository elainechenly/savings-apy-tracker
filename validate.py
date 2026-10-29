from config import APY_MIN, APY_MAX, MAX_DAILY_JUMP, BANKS


def validate(df):
    """Return a list of human-readable issues for the most recent date in the data."""
    if df.empty:
        return ["No data at all."]
    issues = []
    today = df["date"].max()
    t, hist = df[df["date"] == today], df[df["date"] < today]

    # 1) Banks that failed to produce a good number today
    for _, r in t[t["status"] != "ok"].iterrows():
        issues.append(f"[{r['status']}] {r['bank']} / {r['product']} / {r['zip'] or 'national'}: {r['note'][:120]}")

    # 2) Banks that are in config.py but have no row at all today
    seen = set(t["bank"])
    for cfg in BANKS.values():
        if cfg["bank"] not in seen:
            issues.append(f"[missing] {cfg['bank']}: no row today")

    # 3) Range and day-over-day checks on the good rows
    for _, r in t[t["status"] == "ok"].iterrows():
        if not (APY_MIN <= r["apy"] <= APY_MAX):
            issues.append(f"[range] {r['bank']}: APY {r['apy']} outside {APY_MIN}-{APY_MAX}")
        prev = hist[(hist["bank"] == r["bank"]) & (hist["product"] == r["product"])
                    & (hist["zip"] == r["zip"]) & (hist["status"] == "ok")].sort_values("date")
        if len(prev) and abs(r["apy"] - prev.iloc[-1]["apy"]) > MAX_DAILY_JUMP:
            issues.append(f"[jump] {r['bank']}: {prev.iloc[-1]['apy']} -> {r['apy']} (verify manually)")
    return issues
