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
If you have a bank-roll you wish to take positions but don't want to overcommit:
- will enter on positions of breakout/breakthrough of support/resistance

## Getting Started

Clone or download the dollar cost average strategy.

Download & Run to import nzu data.

```bash
python algo.py --noheaders --noprint --symbol ORG
```

View notebook

```
cmd /k "conda activate base && jupyter lab"
```

Comparing multiple strategies
```bash
python strategy-compare.py --noheaders --noprint --symbol TLS --optreturn
```

### Prerequisites

Python
* [Python](https://www.python.org/downloads/)
Anaconda
* [Anaconda](https://www.python.org/downloads/)
Backtrader
* [Backtrader](https://www.python.org/downloads/)