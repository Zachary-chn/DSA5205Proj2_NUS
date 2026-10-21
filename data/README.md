# Data directory

`raw/` contains provider-level daily prices. `processed/` contains deterministic
pipeline outputs. Both directories are generated automatically and their CSV
files are ignored by Git by default.

The production universe has ten assets and approximately nineteen years of
daily observations. Exact row counts are written by the pipeline and must be
reported from the approved final run rather than estimated here.

To freeze data for submission, archive `prices_daily.csv` together with
`run_metadata.json` and a note containing the source, download date, tickers and
date range. Do not replace missing assets or dates silently.

