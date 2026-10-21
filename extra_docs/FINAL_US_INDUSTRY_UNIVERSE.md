# Final U.S. industry ETF universe

## Purpose

The project currently uses one comparable pool of 20 U.S.-listed equity sector and industry ETFs. Every candidate represents an investable part of the U.S. equity market. SPY is included only as the broad-market benchmark and never enters feature ranks, model fitting, or Top-5 selection.

## Inclusion rule

An ETF is included when it:

1. tracks a named U.S. equity sector or industry;
2. was launched before the sample begins in January 2007;
3. has adjusted daily prices for at least 95% of the configured sample dates; and
4. has sufficient history for the one-month trend, six-month relative-strength, and six-month volatility features.

The current list is determined by market exposure, launch date, and data availability. Historical strategy returns are not an inclusion criterion.

## Candidate ETFs

| Group | Ticker | Exposure |
|---|---|---|
| Broad sector | XLY | Consumer discretionary |
| Broad sector | XLP | Consumer staples |
| Broad sector | XLE | Energy |
| Broad sector | XLF | Financials |
| Broad sector | XLV | Health care |
| Broad sector | XLI | Industrials |
| Broad sector | XLK | Information technology |
| Broad sector | XLB | Materials |
| Broad sector | XLU | Utilities |
| Specialised industry | IBB | Biotechnology |
| Specialised industry | IYR | U.S. real estate |
| Specialised industry | ITB | U.S. home construction |
| Specialised industry | KBE | Banks |
| Specialised industry | KRE | Regional banks |
| Specialised industry | XHB | Homebuilders |
| Specialised industry | XME | Metals and mining |
| Specialised industry | XOP | Oil and gas exploration and production |
| Specialised industry | XRT | Retail |
| Specialised industry | SMH | Semiconductors |
| Specialised industry | IYT | Transportation |

## Benchmark and dates

- Benchmark: SPY, buy and hold.
- Raw data source: Yahoo Finance adjusted daily prices.
- Download range: 2007-01-01 through 2026-10-21.
- Formal test signal dates: through 2025-12-31. The additional 2026 prices allow the final 2025 forward return to be formed where required.
- Currency: U.S. dollars.

The exact machine-readable settings are in `configs/final_us_industry_project.yaml`.

## Reference pages

- State Street SPDR sector and industry ETFs: https://www.ssga.com/us/en/intermediary/etfs
- iShares U.S. sector and industry ETFs: https://www.ishares.com/us/products/etf-investments
- VanEck Semiconductor ETF (SMH): https://www.vaneck.com/us/en/investments/semiconductor-etf-smh/
- Yahoo Finance: https://finance.yahoo.com/
