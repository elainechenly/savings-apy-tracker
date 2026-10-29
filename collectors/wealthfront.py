from config import BANKS
from .base import Collector


class Wealthfront(Collector):
    key = "wealthfront"
    locals().update(BANKS[key])
    anchors = ("Cash Account",)
    # Base APY only. The big "4.45% APY" in the hero includes the new-client boost, so we skip it.
    primary = (r"base (\d{1,2}\.\d{1,3})% APY",
               r"(\d{1,2}\.\d{1,3})% Base Annual Percentage Yield",
               r"(\d{1,2}\.\d{1,3})% APY base rate")
