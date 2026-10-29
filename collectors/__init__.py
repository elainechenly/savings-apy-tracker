from .chase import Chase
from .citi import Citi
from .wells_fargo import WellsFargo
from .us_bank import USBank
from .capital_one import CapitalOne
from .amex import Amex
from .wealthfront import Wealthfront
from .marcus import Marcus

# key -> class. main.py loops over this, so adding a bank = new file + one line here.
REGISTRY = {c.key: c for c in (Chase, Citi, WellsFargo, USBank, CapitalOne, Amex, Wealthfront, Marcus)}
