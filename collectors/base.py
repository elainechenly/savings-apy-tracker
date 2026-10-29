"""Shared scraping logic. Philosophy: never guess silently.
If a page shows several different APYs we record a non-ok status and keep
every candidate in `note`, so a human can calibrate the collector."""
import re, datetime as dt, pathlib
from .browser import enter_zip, looks_missing, rate_links, choose_options, click_texts_on

APY_AFTER  = re.compile(r"(\d{1,2}(?:\.\d{1,3})?)\s*%\s*(?:APY|Annual Percentage Yield)", re.I)
APY_BEFORE = re.compile(r"(?:APY|Annual Percentage Yield)\D{0,40}?(\d{1,2}(?:\.\d{1,3})?)\s*%", re.I)
PROMO_WORDS = ("bonus", "boost", "promo", "new client", "new customer", "new to", "introductory",
               "limited time", "limited-time", "referral", "up to", "first 3 months", "first 90 days",
               "relationship", "premier", "private client", "gold", "platinum")


class Collector:
    key = ""
    bank = ""
    product = ""
    url = ""
    alt_urls = ()       # fallbacks tried in order if `url` is a missing page
    scope = "national"  # or "zip"
    anchors = ()
    window = 350
    primary = ()        # regexes (1 capture group = APY) matching ONLY the standard rate
    calibrated = True   # False = never write an APY, only diagnostics
    select_texts = ()   # dropdown choices made BEFORE the ZIP step, e.g. ("Savings",)
    click_texts = ()    # things clicked AFTER the ZIP step (expand a FAQ, open a rate table)
    use_zip = True      # False when the page's only ZIP box is an unrelated branch locator
    wait_for_text = ""  # regex that must appear on the page before we read it (rate tables load late)

    # ---- page access --------------------------------------------------------
    def get_text(self, page, zip_code=None):
        """Open the page (then enter the ZIP on that page). Returns (visible text, log)."""
        log, text = [], ""
        for u in (self.url, *self.alt_urls):
            page.goto(u, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_timeout(4000)
            steps = choose_options(page, self.select_texts)
            zlog = enter_zip(page, zip_code) if (zip_code and self.use_zip) else None
            steps += click_texts_on(page, self.click_texts)
            if self.wait_for_text:
                try:
                    page.get_by_text(re.compile(self.wait_for_text, re.I)).first.wait_for(timeout=20_000)
                    steps.append("rate table loaded")
                except Exception:
                    steps.append(f"'{self.wait_for_text}' never appeared")
            text = page.inner_text("body")
            if looks_missing(text):
                log.append(f"missing page {u}")
                continue
            end = getattr(page, "url", u)
            log.insert(0, f"url={u}" + (f" -> {end}" if end != u else ""))
            log += [x for x in [zlog, *steps] if x]
            break
        return text, "; ".join(log)

    # ---- extraction ---------------------------------------------------------
    def candidates(self, text):
        found = []
        for rx in (APY_AFTER, APY_BEFORE):
            for m in rx.finditer(text):
                lo, hi = max(0, m.start() - 120), min(len(text), m.end() + 120)
                snippet = " ".join(text[lo:hi].split())
                promo = any(w in snippet.lower() for w in PROMO_WORDS)
                found.append((float(m.group(1)), promo, snippet))
        return found

    def focus(self, text):
        if not self.anchors:
            return text
        parts = []
        for a in self.anchors:
            for m in re.finditer(re.escape(a), text, re.I):
                parts.append(text[max(0, m.start() - self.window): m.end() + self.window])
        return "\n".join(parts) or text

    def extract(self, text):
        """Return (apy or None, status, note)."""
        if self.primary:
            vals = [float(v) for rx in self.primary for v in re.findall(rx, text, re.I | re.S)]
            distinct = sorted(set(vals))
            if len(distinct) == 1:
                return distinct[0], "ok", f"primary patterns matched {len(vals)}x -> {distinct[0]}"
            generic = "; ".join(f"{a}{'*' if p else ''}" for a, p, _ in self.candidates(text)[:8])
            if distinct:
                return None, "ambiguous", f"primary patterns disagree {distinct}; generic: {generic}"
            return None, "pattern_missing", f"page layout changed? generic candidates: {generic}"
        cands = self.candidates(self.focus(text))
        if not cands:
            return None, "not_found", "no 'X.XX% APY' on page (blocked? JS not rendered?)"
        base = sorted({a for a, promo, _ in cands if not promo})
        summary = "; ".join(f"{a}{'*' if p else ''}" for a, p, _ in cands[:8])
        if len(base) == 1:
            return base[0], "ok", f"candidates: {summary} (*=promo-like, ignored)"
        if not base:
            return None, "only_promo", f"candidates: {summary}"
        return None, "ambiguous", f"multiple base APYs {base}; candidates: {summary}"

    # ---- runner -------------------------------------------------------------
    def _row(self, state, zip_code, apy, status, note):
        now = dt.datetime.now(dt.timezone.utc)
        return dict(date=now.date().isoformat(), fetched_at=now.isoformat(timespec="seconds"),
                    bank=self.bank, product=self.product, state=state, zip=zip_code or "",
                    apy=apy, rate_type="base", status=status, source_url=self.url, note=note[:600])

    def _dump(self, page, tag, text):
        """Save page text, screenshot and rate-related links to debug/."""
        d = pathlib.Path("debug"); d.mkdir(exist_ok=True)
        (d / f"{tag}.txt").write_text(text, encoding="utf-8")
        try:
            (d / f"{tag}_links.txt").write_text("\n".join(rate_links(page)), encoding="utf-8")
            page.screenshot(path=str(d / f"{tag}.png"), full_page=True)
        except Exception:
            pass

    def collect(self, page, zips, debug=False):
        targets = [("US", None)] if self.scope == "national" else \
                  [(st, z) for st, zs in zips.items() for z in zs]
        rows = []
        for state, z in targets:
            tag = f"{self.key}_{z or 'national'}"
            try:
                text, log = self.get_text(page, z)
                if debug:
                    self._dump(page, tag, text)
                apy, status, note = self.extract(text)
                if z and z not in text:
                    note += f" | WARNING: ZIP {z} not visible on page"
                note = f"{log} | {note}"
                if not self.calibrated:           # diagnostics only: never publish an APY
                    note = f"UNCALIBRATED (generic saw {status} {apy}) | {note}"
                    apy, status = None, "needs_calibration"
            except Exception as e:                 # timeout, bot block, network...
                apy, status, note = None, "error", f"{type(e).__name__}: {str(e)[:200]}"
            rows.append(self._row(state, z, apy, status, note))
        return rows
