# Final U.S. industry ETF universe

## Purpose

The project currently uses one comparable pool of 20 U.S.-listed equity sector and industry ETFs. Every candidate represents an investable part of the U.S. equity market. SPY is included only as the broad-market benchmark and never enters feature ranks, model fitting, or Top-5 selection.

## Selection record and historical-data eligibility

The original selection description used market exposure, launch date, and data availability, and stated that each ETF was launched before January 2007. That statement was too broad for SMH: its saved history includes a predecessor instrument. The following historical-data wording clarifies the retained universe after the SMH investigation; the records do not establish that a predecessor-aware rule was explicitly specified before the ETFs were selected.

For the retained universe, eligibility refers to:

1. exposure to a named U.S. equity sector or industry;
2. usable historical sector/industry investment data beginning before the sample starts in January 2007, potentially including documented predecessor instruments, rather than necessarily the inception of the current ETF;
3. adjusted daily prices for at least 95% of the configured sample dates; and
4. sufficient history for the one-month trend, six-month relative-strength, and six-month volatility features.

The candidate list, saved historical series, coverage threshold, feature requirements, and reported results have not been changed by this documentation clarification. Historical strategy returns are not part of the stated inclusion criteria. Full-sample data availability and retrospective universe selection remain limitations.

## SMH predecessor history and December 2011 transition

Before 21 December 2011, ticker SMH represented Semiconductor HOLDRS Trust. Participating holders exchanged validly tendered HOLDRS receipts for shares of Market Vectors Semiconductor ETF on 20 December 2011, one ETF share per receipt. The new ETF, now named VanEck Semiconductor ETF, began trading under SMH on 21 December 2011. The transition involved portfolio rebalancing and a change of legal instrument; it was not simply the unchanged current ETF operating since before 2007. See the [VanEck exchange notice](https://www.vaneck.com/distributions/etfs/smh-holdrs-transaction-tax-information-Dec2011-pdf/) and [OCC memorandum 29974](https://infomemo.theocc.com/infomemos?date=201112&number=29974).

We retain Yahoo's supplied SMH historical series, including the predecessor period. A read-only inspection of saved Close and Adjusted Close observations for 15–23 December 2011 found no obvious price discontinuity across the transition. The 20–21 December return was approximately -1.1655% in both series, and the Adjusted Close/Close ratio remained approximately stable. A read-only comparison found the saved Close values matched Yahoo's currently returned history for the inspected dates, with only tiny Adjusted Close differences.

These checks support numerical consistency with the documented transition, but do not independently verify Yahoo's complete adjustment/stitching methodology or every investor's realized exchange return, cash flows, taxes, and costs. The saved series spans different instruments and portfolio compositions. This predecessor-history assumption must accompany descriptions of the training data and universe; it is not a claim of identical investment mandates or a newly established pre-selection rule.

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
