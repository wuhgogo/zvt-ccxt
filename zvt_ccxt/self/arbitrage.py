# -*- coding: utf-8 -*-
import time

sleep_time = 3000


def shouldSleep():
    # if (self.isBusy or not exchange.IO("status")) or not ext.IsTrading(self.symbolA):
    sleep(sleep_time)


def sleep(sleeping_time=1000):
    time.sleep(sleeping_time)


class Hedge:

    def __init__(self, q, e, init_account, symbol_a, symbol_b, hedge_spread, cover_spread, op_amount):
        self.q = q
        self.init_account = init_account
        self.status = 0
        self.symbol_a = symbol_a
        self.symbol_b = symbol_b
        self.e = e
        self.is_busy = False
        self.hedge_spread = hedge_spread
        self.cover_spread = cover_spread
        self.op_amount = op_amount
        self.records = []
        self.pre_bar_time = 0

    def poll(self):

        shouldSleep()

        insDetailA = exchange.SetContractType(self.symbol_a)
        if not insDetailA:
            return

        tickerA = exchange.GetTicker()
        if not tickerA:
            return

        insDetailB = exchange.SetContractType(self.symbol_b)
        if not insDetailB:
            return

        tickerB = exchange.GetTicker()
        if not tickerB:
            return

            # 计算差价K线
        r = exchange.GetRecords()
        if not r:
            return
        diff = tickerB["Last"] - tickerA["Last"]
        if r[-1]["Time"] != self.pre_bar_time:
            # 更新
            self.records.append({"Time": r[-1]["Time"], "High": diff, "Low": diff, "Open": diff, "Close": diff, "Volume": 0})
            self.pre_bar_time = r[-1]["Time"]
        if diff > self.records[-1]["High"]:
            self.records[-1]["High"] = diff
        if diff < self.records[-1]["Low"]:
            self.records[-1]["Low"] = diff
        self.records[-1]["Close"] = diff
        ext.PlotRecords(self.records, "diff:B-A")
        ext.PlotHLine(self.hedge_spread if diff > 0 else -self.hedge_spread, "hedgeSpread")
        ext.PlotHLine(self.cover_spread if diff > 0 else -self.cover_spread, "coverSpread")

        LogStatus(_D(), "A卖B买", _N(tickerA["Buy"] - tickerB["Sell"]), "A买B卖", _N(tickerA["Sell"] - tickerB["Buy"]))
        action = 0

        if self.status == 0:
            if (tickerA["Buy"] - tickerB["Sell"]) > self.hedge_spread:
                Log("开仓 A卖B买", tickerA["Buy"], tickerB["Sell"], "#FF0000")
                action = 1
                # 加入图表标记
                ext.PlotFlag(self.records[-1]["Time"], "A卖B买", "O")
            elif (tickerB["Buy"] - tickerA["Sell"]) > self.hedge_spread:
                Log("开仓 B卖A买", tickerB["Buy"], tickerA["Sell"], "#FF0000")
                action = 2
                # 加入图表标记
                ext.PlotFlag(self.records[-1]["Time"], "B卖A买", "O")
        elif self.status == 1 and (tickerA["Sell"] - tickerB["Buy"]) <= self.cover_spread:
            Log("平仓 A买B卖", tickerA["Sell"], tickerB["Buy"], "#FF0000")
            action = 2
            # 加入图表标记
            ext.PlotFlag(self.records[-1]["Time"], "A买B卖", "C")
        elif self.status == 2 and (tickerB["Sell"] - tickerA["Buy"]) <= self.cover_spread:
            Log("平仓 B买A卖", tickerB["Sell"] - tickerA["Buy"], "#FF0000")
            action = 1
            # 加入图表标记
            ext.PlotFlag(self.records[-1]["Time"], "B买A卖", "C")

        if action == 0:
            return

        self.is_busy = True
        tasks = []
        if action == 1:
            tasks.append([self.symbol_a, "sell" if self.status == 0 else "closebuy"])
            tasks.append([self.symbol_b, "buy" if self.status == 0 else "closesell"])
        elif action == 2:
            tasks.append([self.symbol_a, "buy" if self.status == 0 else "closesell"])
            tasks.append([self.symbol_b, "sell" if self.status == 0 else "closebuy"])

        def callBack(task, ret):
            def callBack(task, ret):
                self.is_busy = False
                if task["action"] == "sell":
                    self.status = 2
                elif task["action"] == "buy":
                    self.status = 1
                else:
                    self.status = 0
                    account = _C(exchange.GetAccount)
                    LogProfit(account["Balance"] - self.init_account["Balance"], account)
            self.q.pushTask(self.e, tasks[1][0], tasks[1][1], self.op_amount, callBack)

        self.q.pushTask(self.e, tasks[0][0], tasks[0][1], self.op_amount, callBack)

    def SetHedgeSpread(self, hedgeSpread):
        self.hedge_spread = hedgeSpread
        Log("hedgeSpread修改为：", hedgeSpread)
    def SetCoverSpread(self, coverSpread):
        self.cover_spread = coverSpread
        Log("coverSpread修改为：", coverSpread)

def main():
    SetErrorFilter("ready|login|timeout")
    Log("正在与交易服务器连接...")
    while not exchange.IO("status"):
        Sleep(1000)

    Log("与交易服务器连接成功")
    initAccount = _C(exchange.GetAccount)
    Log(initAccount)
    n = 0

    def callBack(task, ret):
        Log(task["desc"], "成功" if ret else "失败")

    q = ext.NewTaskQueue(callBack)
    p = ext.NewPositionManager()
    if CoverAll:
        Log("开始平掉所有残余仓位...")
        p.CoverAll()
        Log("操作完成")

    t = Hedge(q, exchange, initAccount, SA, SB, HedgeSpread, CoverSpread)
    while True:
        q.poll()
        t.poll()
        cmd = GetCommand()
        if cmd:
            arr = cmd.split(":")
            if arr[0] == "AllCover":
                p.CoverAll()
            elif arr[0] == "SetHedgeSpread":
                t.SetHedgeSpread(float(arr[1]))
            elif arr[0] == "SetCoverSpread":
                t.SetCoverSpread(float(arr[1]))
