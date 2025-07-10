
import backtrader as bt
import numpy as np

class SentimentStrategy(bt.Strategy):
    params = dict(rsi_period=14, macd1=12, macd2=26, macdsig=9)

    def __init__(self):
        self.rsi = bt.ind.RSI(period=self.p.rsi_period)
        self.macd = bt.ind.MACD(period_me1=self.p.macd1,
                                period_me2=self.p.macd2,
                                period_signal=self.p.macdsig)
        self.dataclose = self.datas[0].close

        self.order = None
        self.buy_price = None
        self.buy_comm = None

    def next(self):
        sentiment = np.random.uniform(-1, 1)
        price = self.dataclose[0]
        vwap = (self.data.high[0] + self.data.low[0] + price) / 3

        if self.order:
            return  # wait if an order is pending

        if not self.position:
            if (self.rsi < 35 and self.macd.macd > self.macd.signal and sentiment > 0.4 and price < vwap):
                self.order = self.buy()
            elif (self.rsi > 65 and self.macd.macd < self.macd.signal and sentiment < -0.3 and price > vwap):
                self.order = self.sell()
        else:
            if (self.position.size > 0 and price > self.buy_price * 1.02) or                (self.position.size < 0 and price < self.buy_price * 0.98):
                self.close()
            elif (self.position.size > 0 and price < self.buy_price * 0.98) or                  (self.position.size < 0 and price > self.buy_price * 1.02):
                self.close()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
            elif order.issell():
                self.buy_price = order.executed.price
        self.order = None
