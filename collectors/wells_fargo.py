import re
from config import BANKS
from .base import Collector


class WellsFargo(Collector):
    key = "wells_fargo"
    locals().update(BANKS[key])
    wait_for_text = "Way2Save"
    # Way2Save block: "Balance / Standard Interest Rate / APY / $0 or more / 0.01% / 0.01%" -> capture the APY.
    # The big "Earn 3.25% APY as a new customer" banner is Platinum, new customers, $25,000 minimum: excluded.
    primary = (r"Way2Save\S*\s+Savings\s+Balance\s+Standard Interest Rate\s+Annual Percentage Yield \(APY\)"
               r"\s+\$0 or more\s+[\d.]+%\s+([\d.]+)%",)

    def extract(self, text):
        apy, status, note = super().extract(text)
        other = []
        for label, rx in (
            ("Platinum standard", r"Platinum Savings\s+Standard Interest Rates.*?\$0 or more\s+[\d.]+%\s+([\d.]+)%"),
            ("Platinum w/ Prime Checking", r"When linked to Prime Checking.*?\$0 or more\s+[\d.]+%\s+([\d.]+)%"),
            ("Platinum w/ Premier Checking", r"When linked to Premier Checking.*?\$0 or more\s+[\d.]+%\s+([\d.]+)%"),
            ("Platinum new-customer promo ($25k min, excluded)",
             r"Rates for New Savings Customers.*?\$25,000 or more\s+[\d.]+%\s+([\d.]+)%"),
        ):
            m = re.search(rx, text, re.S)
            if m:
                other.append(f"{label} {m.group(1)}%")
        return apy, status, note + (" | other products: " + "; ".join(other) if other else "")
