## Detecting Pump and Dump Schemes in the Crypto Market: A Practical Implementation

### Introduction

Pump and dump schemes are a form of market manipulation in which the price of a low-cap cryptocurrency is artificially inflated ("pumped") through misleading or exaggerated information, only to be followed by a coordinated sell-off ("dump"), leaving unaware investors with significant losses. This practice is particularly rampant in unregulated and highly volatile markets such as cryptocurrency exchanges.

### Why Pump and Dump is a Problem in Crypto

- **Lack of Regulation**: Many crypto exchanges operate with minimal oversight, allowing manipulative behavior to flourish.
- **Low Liquidity Assets**: Small-cap coins with low trading volume are easily manipulated.
- **Anonymity**: Coordinators can organize pumps through anonymous Telegram/Discord groups.
- **Retail Participation**: Many traders are unaware of the risks and can be drawn in by sudden price movements.

### Objectives of Our Detection Bot

- Identify unusual activity that may precede or indicate a pump event.
- Alert early before the main surge or public announcement.
- Document and log signals for analysis and improvement.

---

### Detection Strategies Implemented

Our bot uses multiple heuristic-based signals to detect early signs of a potential pump:

#### 1. **Volume Spike Detection**
**Why**: Pump organizers begin accumulating the coin, leading to an unusual increase in quote volume.
**How**: We calculate the average volume over a historical window and trigger a signal if the current volume exceeds a multiple (e.g., 5x).

#### 2. **Trade Burst Detection**
**Why**: Coordinated purchases lead to a rapid increase in the number of trades.
**How**: If the number of trades in the recent window exceeds a threshold (e.g., 10 trades), we consider it suspicious.

#### 3. **Price Drift Detection**
**Why**: Slow, sustained price increases are often seen before the main pump.
**How**: Track price over a sliding window; if the price increases significantly, raise suspicion.

#### 4. **Order Book Buy Wall Stacking**
**Why**: Organizers create artificial demand by stacking small buy orders below the current price to make the market look stronger.
**How**: Analyze the order book for a concentration of bids below the last traded price.

---

### Technical Design

- **Exchange**: The bot uses real-time data from KuCoin via the `ccxt` library.
- **Logging**: All signals with timestamps are stored in a CSV file for analysis.
- **Alerts**: Suspicious events are sent via Telegram.
- **Visualization**: Real-time matplotlib dashboards show price and volume trends.
- **Concurrency**: Uses `ThreadPoolExecutor` for parallel scanning of coins.

---

### Conclusion and Next Steps

This MVP provides a robust framework for early detection of pump and dump schemes using simple market signals. Future improvements can include:

- Machine learning for more accurate pattern recognition.
- Real-time web dashboards for monitoring.
- Order book depth heatmaps.

Understanding and detecting manipulation in real time is key to protecting market participants and increasing transparency in crypto markets.

