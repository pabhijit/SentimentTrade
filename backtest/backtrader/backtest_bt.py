
import backtrader as bt
import datetime
from strategy import SentimentStrategy

# Create a backtrader engine
cerebro = bt.Cerebro()
cerebro.addstrategy(SentimentStrategy)

# Load data
data = bt.feeds.GenericCSVData(
    dataname='data/test_data.csv',
    dtformat='%Y-%m-%d %H:%M:%S',
    timeframe=bt.TimeFrame.Minutes,
    compression=1,
    openinterest=-1,
    headers=True
)
cerebro.adddata(data)

# Set initial capital
cerebro.broker.setcash(100000.0)

# Run
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Plot result
cerebro.plot(style='candlestick')
