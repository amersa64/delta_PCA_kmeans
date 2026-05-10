airline-miles-collector
=======================

Tiny script to file retroactive missing-mileage requests with American, United,
Delta, and JetBlue, driven from a CSV of flights you took.

Setup:

    pip install -r requirements.txt
    playwright install chromium

Run:

    python collect.py                  # all rows whose Status starts with MISSING
    python collect.py --airline AA     # one airline at a time (AA / UA / DL / B6)
    python collect.py --dry            # open the form URLs only, don't fill
    python collect.py --include-verify # also process rows marked "Verify credit"

The script opens a real Chromium window. For each actionable row it loads that
airline's missing-miles form, fills the fields it can, and pauses. You review
the form, click Submit yourself, then press Enter to move to the next row
(or 's' + Enter to skip without submitting).

UA, DL, and B6 forms require a logged-in session. The first time the script
hits each of those airlines, it pauses so you can sign in (and navigate to the
form, since Delta puts it behind My SkyMiles → Request Mileage Credit). The
session persists for the rest of the run. AA's request-flight-miles form is
public.

Rows are skipped automatically when:

  - Status is `Verify credit` (might already be credited; rerun with
    `--include-verify` if you've checked and they aren't)
  - Status is `VERIFY OWNERSHIP first` (rows 22-23, flagged risky)
  - Date / Flight # / Origin / Destination is `TBD`

For AA rows, the script prompts once for the full AAdvantage # (the CSV only
has the first 3 digits) and reuses it.

Selectors and form URLs change. If a field doesn't fill, grep for the
input's `name=` in devtools and update the relevant `fill_*` function in
`collect.py`. URLs live in the `URLS` dict at the top of the file.

---

Legacy: this repo previously contained a 2014 PCA/k-means analysis of Delta
fleet specs (`delta.R`, `delta.csv`); those files are kept for posterity.
