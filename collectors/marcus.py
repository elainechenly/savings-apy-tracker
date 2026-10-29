from config import BANKS
from .base import Collector


class Marcus(Collector):
    key = "marcus"
    locals().update(BANKS[key])
    anchors = ("Online Savings", "High-Yield Savings")
    # Hero rate, plus the "current high-yield rate of X% APY" sentence.
    # Deliberately NOT matching the comparison calculator (0.40%, 0.04%) or the 3.75% referral example.
    primary = (r"(\d{1,2}\.\d{1,3})%\s*APY\s+Online Savings Account Annual Percentage Yield",
               r"current high-yield rate of (\d{1,2}\.\d{1,3})% APY")
