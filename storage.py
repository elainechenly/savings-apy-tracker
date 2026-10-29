import pandas as pd, pathlib

COLUMNS = ["date", "fetched_at", "bank", "product", "state", "zip", "apy",
           "rate_type", "status", "source_url", "note"]
KEY = ["date", "bank", "product", "zip"]      # one row per day / bank / product / ZIP


def load(path):
    """Read the CSV (or an empty table if it doesn't exist yet)."""
    p = pathlib.Path(path)
    if not p.exists():
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(p, dtype={"zip": str}, keep_default_na=False)   # keep ZIPs like "98005" as text
    df["apy"] = pd.to_numeric(df["apy"], errors="coerce")             # blank apy -> NaN
    return df


def upsert(rows, path):
    """Add today's rows. Idempotent: re-running on the same day replaces that day's rows."""
    new = pd.DataFrame(rows, columns=COLUMNS)
    # df = pd.concat([load(path), new], ignore_index=True)
    old = load(path)
    df = new if old.empty else pd.concat([old, new], ignore_index=True)
    df = df.drop_duplicates(KEY, keep="last").sort_values(["date", "bank", "product", "zip"])
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
