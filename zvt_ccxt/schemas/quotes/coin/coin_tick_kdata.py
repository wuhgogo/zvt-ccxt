# -*- coding: utf-8 -*-
# this file is generated by gen_kdata_schema function, dont't change it
from sqlalchemy.ext.declarative import declarative_base

from zvt.contract.register import register_schema
from zvt_ccxt.schemas.quotes import CoinTickCommon

KdataBase = declarative_base()


class CoinTickKdata(KdataBase, CoinTickCommon):
    __tablename__ = 'coin_tick_kdata'


register_schema(providers=['ccxt'], db_name='coin_tick_kdata', schema_base=KdataBase)

__all__ = ['CoinTickKdata']