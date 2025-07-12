import backtrader as bt
import numpy as np
class SentimentStrategy(bt.Strategy):
    params = dict(rsi_period=14, macd1=12, macd2=26, macdsig=9, atr_period=14)
    def __init__(self):
        self.rsi = bt.ind.RSI(period=self.p.rsi_period)
        self.macd = bt.ind.MACD(period_me1=self.p.macd1,
                                period_me2=self.p.macd2,
                                period_signal=self.p.macdsig)
        self.atr = bt.ind.ATR(period=self.p.atr_period)
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.order = None
        self.buy_price = None
    def next(self):
        sentiment = np.random.uniform(-1, 1)
        price = self.dataclose[0]
        vwap = (self.datahigh[0] + self.datalow[0] + price) / 3
        if self.order:
            return  # wait if an order is pending
        if not self.position:
            if (self.rsi < 35 and self.macd.macd > self.macd.signal and sentiment > 0.4 and price < vwap):
                sl = price - 1.5 * self.atr[0]
                tp = price + 2 * self.atr[0]
                self.buy_price = price
                self.order = self.buy()
                self.sell(price=tp, exectype=bt.Order.Limit)
                self.sell(price=sl, exectype=bt.Order.Stop)
            elif (self.rsi > 65 and self.macd.macd < self.macd.signal and sentiment < -0.3 and price > vwap):
                sl = price + 1.5 * self.atr[0]
                tp = price - 2 * self.atr[0]
                self.buy_price = price
                self.order = self.sell()
                self.buy(price=tp, exectype=bt.Order.Limit)
                self.buy(price=sl, exectype=bt.Order.Stop)
        else:
            # Optional: exit rule overrides for testing
            if (self.position.size > 0 and price > self.buy_price * 1.02) or                (self.position.size < 0 and price < self.buy_price * 0.98):
                self.close()
            elif (self.position.size > 0 and price < self.buy_price * 0.98) or                  (self.position.size < 0 and price > self.buy_price * 1.02):
                self.close()
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy() or order.issell():
                self.buy_price = order.executed.price
        self.order = None
