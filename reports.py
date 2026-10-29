import json, pathlib


def build_dashboard(df, out):
    """Fill template.html with the CSV data and write the finished page to `out`."""
    recs = df[["date", "bank", "product", "state", "zip", "apy", "status"]].copy()
    recs["apy"] = recs["apy"].astype(object).where(recs["apy"].notna(), None)   # NaN -> null in JSON
    template = pathlib.Path("template.html").read_text(encoding="utf-8")
    html = template.replace("__DATA__", json.dumps(recs.to_dict("records")))
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
