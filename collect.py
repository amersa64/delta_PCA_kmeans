"""
Open each airline's missing-miles form pre-filled with what we have from
flights.csv, then pause so you can review and click Submit yourself.

Usage:
    python collect.py                  # all rows whose Status starts with MISSING
    python collect.py --airline AA     # one airline (AA, UA, DL, B6)
    python collect.py --dry            # open form URLs without filling, just to check them
    python collect.py --include-verify # also try rows marked "Verify credit"
"""

import argparse
import csv
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

CSV_PATH = Path(__file__).parent / "flights.csv"

# Missing-miles forms. URLs drift; if one 404s, grep for the airline's
# "request mileage credit" page and update.
URLS = {
    "AA": "https://www.aa.com/forms/request-flight-miles/",
    "UA": "https://www.united.com/en/us/mileageplus/mileagecredit/",
    "DL": "https://www.delta.com/us/en/need-help/support-skymiles",
    "B6": "https://trueblue.jetblue.com/request-points",
}

# UA, DL, B6 require a logged-in session. AA's form is public.
NEEDS_LOGIN = {"UA", "DL", "B6"}

AIRLINE_CODE = {
    "American Airlines": "AA",
    "United Airlines":   "UA",
    "Delta Air Lines":   "DL",
    "JetBlue":           "B6",
}

REQUIRED = ("Date", "Flight #", "Origin", "Destination")


def is_tbd(value: str) -> bool:
    return not value or value.strip().upper().startswith("TBD")


def row_actionable(row: dict) -> tuple[bool, str]:
    for field in REQUIRED:
        if is_tbd(row[field]):
            return False, f"{field} is TBD"
    return True, ""


def prompt_continue(row_id: str) -> str:
    return input(
        f"Row {row_id}: review the form, click Submit in the browser, "
        f"then press Enter (or 's' + Enter to skip without submitting): "
    ).strip().lower()


# Each fill_* takes the page (already navigated to the form URL) and the row.
# Selectors are best-effort guesses against current public forms; verify on
# first run with --headed and patch as needed.

def fill_aa(page: Page, row: dict, ff_number: str) -> None:
    # AA's form fields (as of last check): firstName, lastName, aaNumber,
    # ticketNumber, flightNumber, departureDate, originAirport, destinationAirport.
    safe_fill(page, 'input[name="firstName"]',         "Amer")
    safe_fill(page, 'input[name="lastName"]',          "Alsabbagh")
    safe_fill(page, 'input[name="aaNumber"]',          ff_number)
    safe_fill(page, 'input[name="flightNumber"]',      row["Flight #"].replace("AA ", "").strip())
    safe_fill(page, 'input[name="departureDate"]',     row["Date"])
    safe_fill(page, 'input[name="originAirport"]',     row["Origin"])
    safe_fill(page, 'input[name="destinationAirport"]', row["Destination"])


def fill_ua(page: Page, row: dict) -> None:
    safe_fill(page, 'input[name="mileagePlusNumber"]', row["Member #"])
    safe_fill(page, 'input[name="flightNumber"]',      row["Flight #"].replace("UA", "").strip())
    safe_fill(page, 'input[name="flightDate"]',        row["Date"])
    safe_fill(page, 'input[name="originAirport"]',     row["Origin"])
    safe_fill(page, 'input[name="destinationAirport"]', row["Destination"])
    safe_fill(page, 'input[name="confirmationNumber"]', row["PNR / Conf Code"])


def fill_dl(page: Page, row: dict) -> None:
    safe_fill(page, 'input[name="skymilesNumber"]',    row["Member #"])
    safe_fill(page, 'input[name="ticketNumber"]',      row["PNR / Conf Code"])
    safe_fill(page, 'input[name="flightNumber"]',      row["Flight #"].replace("DL", "").strip())
    safe_fill(page, 'input[name="flightDate"]',        row["Date"])
    safe_fill(page, 'input[name="originAirport"]',     row["Origin"])
    safe_fill(page, 'input[name="destinationAirport"]', row["Destination"])


def fill_b6(page: Page, row: dict) -> None:
    safe_fill(page, 'input[name="trueBlueNumber"]',    row["Member #"])
    safe_fill(page, 'input[name="confirmationCode"]',  row["PNR / Conf Code"])
    safe_fill(page, 'input[name="flightNumber"]',      row["Flight #"])
    safe_fill(page, 'input[name="flightDate"]',        row["Date"])
    safe_fill(page, 'input[name="originAirport"]',     row["Origin"])
    safe_fill(page, 'input[name="destinationAirport"]', row["Destination"])


def safe_fill(page: Page, selector: str, value: str) -> None:
    try:
        page.fill(selector, value, timeout=2000)
    except Exception as e:
        print(f"  ! could not fill {selector!r}: {e.__class__.__name__}")


FILLERS = {"AA": fill_aa, "UA": fill_ua, "DL": fill_dl, "B6": fill_b6}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--airline", choices=["AA", "UA", "DL", "B6"], help="filter to one airline")
    p.add_argument("--dry", action="store_true", help="open URLs only, don't fill")
    p.add_argument("--include-verify", action="store_true",
                   help="also process rows whose Status is 'Verify credit'")
    return p.parse_args()


def should_process(row: dict, include_verify: bool) -> bool:
    status = row["Status"].strip()
    if status.startswith("MISSING"):
        return True
    if include_verify and status == "Verify credit":
        return True
    return False


def main() -> int:
    args = parse_args()
    rows = list(csv.DictReader(CSV_PATH.open()))

    counts = {"submitted_or_skipped_by_user": 0, "skipped_status": 0,
              "skipped_tbd": 0, "skipped_unknown_airline": 0, "errors": 0}

    aa_ff_number = ""
    logged_in: set[str] = set()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        for row in rows:
            rid = row["ID"]
            code = AIRLINE_CODE.get(row["Airline"])
            if not code:
                print(f"Row {rid}: unknown airline {row['Airline']!r}, skipping")
                counts["skipped_unknown_airline"] += 1
                continue
            if args.airline and code != args.airline:
                continue
            if not should_process(row, args.include_verify):
                print(f"Row {rid}: status={row['Status']!r}, skipping")
                counts["skipped_status"] += 1
                continue
            ok, why = row_actionable(row)
            if not ok:
                print(f"Row {rid}: {why}, skipping")
                counts["skipped_tbd"] += 1
                continue

            print(f"\nRow {rid}: {code} {row['Flight #']} {row['Origin']}->{row['Destination']} on {row['Date']}")
            try:
                page.goto(URLS[code], timeout=30000)
            except Exception as e:
                print(f"  ! failed to load {URLS[code]}: {e}")
                counts["errors"] += 1
                continue

            if code in NEEDS_LOGIN and code not in logged_in:
                input(f"  log in to {code} in the browser, navigate to the missing-miles form, then press Enter ")
                logged_in.add(code)

            if args.dry:
                input("  --dry: form loaded; press Enter for next row ")
                continue

            if code == "AA":
                if not aa_ff_number:
                    aa_ff_number = input("  AA AAdvantage # (full number, asked once): ").strip()
                fill_aa(page, row, aa_ff_number)
            else:
                FILLERS[code](page, row)

            answer = prompt_continue(rid)
            if answer != "s":
                counts["submitted_or_skipped_by_user"] += 1

        browser.close()

    print("\n--- summary ---")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
