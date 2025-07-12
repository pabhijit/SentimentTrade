import backtrader as bt

class TurnoverAnalyzer(bt.Analyzer):
    def __init__(self):
        self.total_traded_value = 0.0
        self.total_days = 0
        self.initial_value = 0.0

    def start(self):
        self.initial_value = self.strategy.broker.getvalue()

    def notify_trade(self, trade):
        if trade.isclosed:
            self.total_traded_value += abs(trade.price * trade.size)

    def stop(self):
        final_value = self.strategy.broker.getvalue()
        avg_value = (self.initial_value + final_value) / 2
        turnover = self.total_traded_value / avg_value if avg_value else 0
        self.rets['turnover'] = turnover
