import re
from config import BANKS
from .base import Collector


class USBank(Collector):
    key = "us_bank"
    locals().update(BANKS[key])
    click_texts = ("all the rates",)     # opens the rate sheet for the ZIP we entered
    wait_for_text = "Standard APY"       # the rate table loads after the click and the ZIP step
    # Rate sheet: "Bank Smartly Savings / Standard interest rate / Standard APY / 0.05% / 0.05%".
    # The 1.00%-3.50% "relationship" rows need a qualifying checking account and are excluded.
    primary = (r"Bank Smartly Savings\s+Standard interest rate\s+Standard APY\s+[\d.]+%\s+([\d.]+)%",)

    def extract(self, text):
        apy, status, note = super().extract(text)
        rel = re.findall(r"\$[\d,]+\+?\s+(?:to \$[\d,.]+\s+)?[^\n]*?\s+[\d.]+%\s+[\d.]+%\s+([\d.]+)%", text)
        if rel:
            note += f" | relationship APYs {min(map(float, rel)):.2f}%-{max(map(float, rel)):.2f}% (need checking acct, excluded)"
        return apy, status, note
