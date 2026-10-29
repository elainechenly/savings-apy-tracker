from config import BANKS
from .base import Collector


class CapitalOne(Collector):
    key = "capital_one"
    locals().update(BANKS[key])
    anchors = ("360 Performance Savings", "Performance Savings")
    # Footnote: "A rate of X% APY applies to all account balances."
    # Discover savings now lives here too, so there is no separate Discover collector.
    primary = (r"rate of (\d{1,2}\.\d{1,3})% Annual Percentage Yield \(APY\) applies to all account balances",)
