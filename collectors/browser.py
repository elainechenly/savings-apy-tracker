"""Browser helpers: dropdowns, ZIP entry, clicks, missing-page detection and link discovery."""
import re

ZIP_INPUT = ('input[placeholder*="zip" i], input[aria-label*="zip" i], input[name*="zip" i], '
             'input[id*="zip" i], input[autocomplete="postal-code"]')
CHANGE = re.compile(r"^\s*(edit|change)\s*$", re.I)
CONFIRM = re.compile(r"^\s*(ok|go|next|submit|apply|update|continue|confirm|save)\s*$", re.I)
MISSING_MARKERS = ("information isn't here", "page not found", "has either moved or does not exist",
                   "404 not_found", "404 not found")


def looks_missing(text):
    t = text.lower()
    return any(m in t for m in MISSING_MARKERS) or len(t.strip()) < 40


def _visible_zip_box(page):
    for el in page.query_selector_all(ZIP_INPUT):
        try:
            if el.is_visible():
                return el
        except Exception:
            pass
    return None


def choose_options(page, wanted):
    """For each word in `wanted`, pick the matching option in a visible <select> (e.g. Citi's rate-type menu)."""
    notes = []
    for word in wanted:
        done = False
        for sel in page.query_selector_all("select"):
            try:
                for opt in sel.query_selector_all("option"):
                    if re.search(word, opt.inner_text() or "", re.I):
                        sel.select_option(value=opt.get_attribute("value"))
                        page.wait_for_timeout(2500)
                        done = True
                        break
            except Exception:
                pass
            if done:
                break
        notes.append(f"selected '{word}'" if done else f"no dropdown option '{word}'")
    return notes


def enter_zip(page, zip_code):
    """Best effort: find a visible ZIP box (clicking an 'Edit'/'Change' link first if needed),
    type the ZIP and confirm it (Enter + any OK/Next/Go button). Returns a short log for the CSV note."""
    box = _visible_zip_box(page)
    if box is None:
        try:
            page.get_by_text(CHANGE).first.click(timeout=3000)
            page.wait_for_timeout(1500)
            box = _visible_zip_box(page)
        except Exception:
            pass
    if box is None:
        return "ZIP box not found"
    try:
        box.fill(zip_code)
        box.press("Enter")
        page.wait_for_timeout(1000)
        clicked = ""
        try:
            page.get_by_role("button", name=CONFIRM).first.click(timeout=2000)
            clicked = " + clicked confirm button"
        except Exception:
            pass
        page.wait_for_timeout(3500)
        return "ZIP typed" + clicked
    except Exception as e:
        return f"ZIP entry failed: {type(e).__name__}"


def click_texts_on(page, texts):
    """Click the first element containing each text (expand a FAQ, open a rate table...)."""
    notes = []
    for t in texts:
        try:
            page.get_by_text(re.compile(t, re.I)).first.click(timeout=3000)
            page.wait_for_timeout(1500)
            notes.append(f"clicked '{t}'")
        except Exception:
            notes.append(f"could not click '{t}'")
    return notes


def rate_links(page):
    """Links whose text or address mentions rate / APY / savings (helps us find the right rate page)."""
    out = set()
    for a in page.query_selector_all("a[href]"):
        try:
            text = " ".join((a.inner_text() or "").split())
            href = a.get_attribute("href") or ""
            if re.search(r"rate|apy|savings", f"{text} {href}", re.I):
                out.add(f"{text[:70]} -> {href}")
        except Exception:
            pass
    return sorted(out)
