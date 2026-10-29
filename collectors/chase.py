from config import BANKS
from .base import Collector


class Chase(Collector):
    key = "chase"
    locals().update(BANKS[key])
    wait_for_text = "All Balances"        # basic Chase Savings rate page, entered with the ZIP
    # Table: "BALANCE / INTEREST RATE / ANNUAL PERCENTAGE YIELD / All Balances  0.01%  0.01%" -> capture the APY.
    primary = (r"All Balances\s+[\d.]+%\s+([\d.]+)%",)
