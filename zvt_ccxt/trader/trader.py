# -*- coding: utf-8 -*-
import json
import logging
from typing import List, Union

import pandas as pd

from zvt.trader.trader import Trader
from zvt_ccxt.domain import Coin


class CoinTrader(Trader):
    entity_schema = Coin
