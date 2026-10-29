import re
from config import BANKS
from .base import Collector

# Headers carry footnote marks ("APY3†", "Rate3†"), so match them with \S* instead of assuming punctuation only.
BOOST = r"{}.*?Premium Boost Rates\s+APY\S*\s+Interest Rate\S*\s+([\d.]+)%"


class Citi(Collector):
    key = "citi"
    locals().update(BANKS[key])
    wait_for_text = "Standard APY"
    # Base tier = "Everyday Benefits" (combined balance $0-$29,999.99). Its table reads:
    #   "Citi Savings / Standard APY / Standard Interest Rate / 0.05% / 0.05%"  -> the first number is the APY.
    # Anchoring on "Everyday Benefits" + "Designed for" skips the later tiers' own "Standard" tables.
    primary = (r"Everyday Benefits\s+Designed for customers.*?Citi Savings\s+Standard APY\S*\s+Standard Interest Rate\S*\s+([\d.]+)%\s+[\d.]+%",)

    def extract(self, text):
        apy, status, note = super().extract(text)
        other = []
        for label, name in (("Priority tier ($30k+)", r"Citi Priority Relationship Tier"),
                            ("Citigold tier ($200k+)", r"Citigold\W{0,3}\s+Relationship Tier"),
                            ("Private Client tier ($1M+)", r"Citigold\W{0,3}\s+Private Client Relationship Tier")):
            m = re.search(BOOST.format(name), text, re.S)
            if m:
                other.append(f"{label} boost {m.group(1)}%")
        if other:
            note += " | other tiers (not regular customer, excluded): " + "; ".join(other)
        return apy, status, note
