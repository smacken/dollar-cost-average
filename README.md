# Dollar cost average
- trading strategy

Simple example of a dollar cost average trading strategy.

![Dollar cost average plot](https://raw.githubusercontent.com/smacken/dollar-cost-average/master/docfx/example.PNG)

Dollar Cost by Time
Given a certain amount invested every month:
- will buy if the market is bullish
- will carry-over any remainder from unfulfilled previous months
- will stop taking positions if the market turns bearish
- will implement a stop-loss to exit position if market turns bullish > bearish (ATR % trailing-stop)

Dollar Cost by Price
If you have a bank-roll you wish to take positions but don't want to overcommit too early:
- will enter on positions of breakout/breakthrough of support/resistance

## Getting Started

Clone or download the dollar cost average strategy.

Download & Run to import nzu data.

```bash
python algo.py --noheaders --noprint --symbol ORG
```

View notebook

```
cmd /k "conda activate dollarcost && jupyter lab"
```

Comparing multiple strategies
```bash
python strategy-compare.py --noheaders --noprint --symbol TLS --optreturn
```

Strategy benchmarking
A number of benchmark strategies exist to better understand the quality of any algo created.
- Buy & Hold - benchmarks 100% initial bankroll allocation
- Buy & Hold Dollar cost - benchmarks a fund-like monthly allocation

To include a strategy in the comparison adorn it with the strategy fetcher register decorator.
```python
@StrategyFetcher.register
class BuyAndHoldDollarCost(bt.Strategy):
```

![Strategy compare](https://raw.githubusercontent.com/smacken/dollar-cost-average/master/docfx/compare.PNG)

### Prerequisites

* [Python](https://www.python.org/downloads/)
* [Anaconda](https://www.python.org/downloads/)
* [Backtrader](https://www.python.org/downloads/)

### Installing

Run install.bat to setup environment. Or:
```bash
pip install -r requirements.txt
```