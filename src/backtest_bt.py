# Backtesting Script using Backtrader

import backtrader as bt
import datetime
from strategy import SentimentStrategy
from turnover import TurnoverAnalyzer

# Engine setup
cerebro = bt.Cerebro()
cerebro.addstrategy(SentimentStrategy)

# Data
data = bt.feeds.GenericCSVData(
    dataname='data/test_data.csv',
    dtformat='%Y-%m-%d %H:%M:%S',
    timeframe=bt.TimeFrame.Minutes,
    compression=1,
    openinterest=-1,
    headers=True
)
cerebro.adddata(data)
cerebro.broker.setcash(100000.0)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual')
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
cerebro.addanalyzer(TurnoverAnalyzer, _name='turnover')

# Run
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
results = cerebro.run()
strat = results[0]
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Results
print("\n--- Performance Metrics ---")
print("Sharpe Ratio:", strat.analyzers.sharpe.get_analysis())
print("Drawdown:", strat.analyzers.drawdown.get_analysis())
print("Trade Summary:", strat.analyzers.trades.get_analysis())
print("Annual Returns:", strat.analyzers.annual.get_analysis())
print("SQN Score:", strat.analyzers.sqn.get_analysis())
print("Turnover:", strat.analyzers.turnover.get_analysis())

# Plot chart
cerebro.plot(style='candlestick')
