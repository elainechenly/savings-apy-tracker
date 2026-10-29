from config import BANKS
from .base import Collector


class Amex(Collector):
    key = "amex"
    locals().update(BANKS[key])
    anchors = ("High Yield Savings",)
    # The HYSA box only. The "up to 4.40% APY" next to it is the CD rate and is ignored.
    primary = (r"High Yield Savings \(HYSA\)\s*(\d{1,2}\.\d{1,3})% APY",)
