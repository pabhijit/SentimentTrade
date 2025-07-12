import backtrader as bt

class MomentumStrategy(bt.Strategy):
    params = dict(fast_ma=10, slow_ma=30)

    def __init__(self):
        # === Indicators ===
        self.ma_fast = bt.ind.SMA(period=self.p.fast_ma)
        self.ma_slow = bt.ind.SMA(period=self.p.slow_ma)

        # === Internal state ===
        self.order = None

    def next(self):
        # === Wait if an order is pending ===
        if self.order:
            return

        # === Entry logic ===
        if not self.position:
            # Buy signal: fast MA crosses above slow MA
            if self.ma_fast[0] > self.ma_slow[0] and self.ma_fast[-1] <= self.ma_slow[-1]:
                self.order = self.buy()
            # Sell signal: fast MA crosses below slow MA
            elif self.ma_fast[0] < self.ma_slow[0] and self.ma_fast[-1] >= self.ma_slow[-1]:
                self.order = self.sell()

        # === Exit logic ===
        else:
            # Exit long on bearish crossover
            if self.position.size > 0 and self.ma_fast[0] < self.ma_slow[0]:
                self.close()
            # Exit short on bullish crossover
            elif self.position.size < 0 and self.ma_fast[0] > self.ma_slow[0]:
                self.close()

    def notify_order(self, order):
        # === Track order status ===
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None