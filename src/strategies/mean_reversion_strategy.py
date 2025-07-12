import backtrader as bt

class MeanReversionStrategy(bt.Strategy):
    params = dict(period=20, devfactor=2)

    def __init__(self):
        # === Indicators ===
        self.bb = bt.ind.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)

        # === Internal state ===
        self.order = None

    def next(self):
        # === Wait if an order is pending ===
        if self.order:
            return

        # === Entry logic ===
        if not self.position:
            # Buy signal: price below lower Bollinger Band
            if self.data.close[0] < self.bb.lines.bot[0]:
                self.order = self.buy()
            # Sell signal: price above upper Bollinger Band
            elif self.data.close[0] > self.bb.lines.top[0]:
                self.order = self.sell()

        # === Exit logic ===
        else:
            # Close long when price reverts to midline
            if self.position.size > 0 and self.data.close[0] > self.bb.lines.mid[0]:
                self.close()
            # Close short when price reverts to midline
            elif self.position.size < 0 and self.data.close[0] < self.bb.lines.mid[0]:
                self.close()

    def notify_order(self, order):
        # === Track order status ===
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None