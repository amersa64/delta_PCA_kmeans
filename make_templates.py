"""
Generate the two XLSX templates this project uses:

  - buyer_outreach_kit.xlsx        : buyer list + pre-written personalized emails
  - may2026_freelance_leads.xlsx   : the deliverable you send buyers after they pay

Each file gets a header row + a few example rows so the schema is obvious.
Replace the example rows with your real data, then run send_emails.py.

The example outreach emails use the placeholders [Your name] and [Your contact
link] — do one find-and-replace pass in your spreadsheet before sending.
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


HERE = Path(__file__).resolve().parent

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="305496")
WRAP = Alignment(wrap_text=True, vertical="top")


def style_header(ws, ncols):
    for col in range(1, ncols + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
    ws.freeze_panes = "A2"


def autosize(ws, max_width=60):
    for col in ws.columns:
        letter = col[0].column_letter
        longest = 0
        for cell in col:
            v = "" if cell.value is None else str(cell.value)
            for line in v.splitlines() or [""]:
                longest = max(longest, len(line))
        ws.column_dimensions[letter].width = min(longest + 2, max_width)


def write_buyer_outreach_kit(path: Path):
    """36 sendable rows + 10 link-only rows = 46 total, matching the spec."""
    wb = Workbook()
    ws = wb.active
    ws.title = "buyers"

    headers = ["Name", "Email", "Source", "Link", "Subject", "Body", "Notes"]
    ws.append(headers)

    # --- example sendable rows (have an Email — script will auto-send these) ---
    examples_sendable = [
        {
            "Name":    "Alex Rivera",
            "Email":   "alex@example.com",
            "Source":  "r/forhire",
            "Link":    "https://reddit.com/r/forhire/comments/example1",
            "Subject": "Quick one — 50 freelance leads for May 2026",
            "Body": (
                "Hey Alex,\n\n"
                "Saw your r/forhire post looking for backend gigs. I put together a "
                "list of 50 hiring posts from this month that match — direct contact, "
                "budget range, and the original link for each.\n\n"
                "$49 flat. Sample row: a YC-backed startup looking for a Django "
                "contractor at $80–120/hr.\n\n"
                "Want the full sheet? Reply and I'll send a Stripe link.\n\n"
                "[Your name]\n"
                "[Your contact link]"
            ),
            "Notes": "Replied to a backend post 3 days ago — warm.",
        },
        {
            "Name":    "Jordan Kim",
            "Email":   "jordan.kim@example.com",
            "Source":  "HN April freelancer thread",
            "Link":    "https://news.ycombinator.com/item?id=example2",
            "Subject": "May 2026 freelance leads — React/TypeScript focused",
            "Body": (
                "Hi Jordan,\n\n"
                "Your April \"seeking work\" comment mentioned React + TS. I have "
                "this month's batch of 50 hiring posts filtered for that stack — "
                "direct emails, budgets, and source links.\n\n"
                "$49 one-time. Reply if you want the Stripe link and I'll send "
                "the file as soon as you pay.\n\n"
                "[Your name]\n"
                "[Your contact link]"
            ),
            "Notes": "",
        },
        {
            "Name":    "Sam Patel",
            "Email":   "sam@example.com",
            "Source":  "r/forhire",
            "Link":    "https://reddit.com/r/forhire/comments/example3",
            "Subject": "50 May freelance leads, $49",
            "Body": (
                "Hey Sam,\n\n"
                "Quick pitch: 50 hand-vetted freelance hiring posts for May 2026, "
                "with direct contact info. $49.\n\n"
                "If interested I'll send a Stripe link and the file lands in your "
                "inbox the second payment clears.\n\n"
                "[Your name]\n"
                "[Your contact link]"
            ),
            "Notes": "",
        },
    ]

    # --- example link-only rows (no Email — script skips these; you DM them manually) ---
    examples_link_only = [
        {
            "Name":    "user_dev_42",
            "Email":   "",
            "Source":  "r/forhire",
            "Link":    "https://reddit.com/r/forhire/comments/example4",
            "Subject": "",
            "Body":    "",
            "Notes":   "No email — DM via Reddit.",
        },
        {
            "Name":    "freelance_throwaway",
            "Email":   "",
            "Source":  "HN",
            "Link":    "https://news.ycombinator.com/user?id=example5",
            "Subject": "",
            "Body":    "",
            "Notes":   "No email — reply to their HN comment.",
        },
    ]

    for r in examples_sendable + examples_link_only:
        ws.append([r[h] for h in headers])

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = WRAP

    style_header(ws, len(headers))
    autosize(ws)
    # Body and Subject benefit from extra width
    ws.column_dimensions["E"].width = 50
    ws.column_dimensions["F"].width = 70

    wb.save(path)


def write_freelance_leads(path: Path):
    """The deliverable file. Schema reflects what a buyer is paying $49 for."""
    wb = Workbook()
    ws = wb.active
    ws.title = "leads"

    headers = [
        "Posted", "Source", "Role", "Stack", "Budget",
        "Contact", "Original Link", "Notes",
    ]
    ws.append(headers)

    examples = [
        ["2026-05-02", "r/forhire", "Senior Django Contractor",
         "Django, Postgres, Stripe", "$80–120/hr",
         "hiring@startup.example", "https://reddit.com/r/forhire/comments/lead1",
         "YC-backed; 3-month engagement."],
        ["2026-05-03", "HN Who's Hiring", "React/TS Frontend Engineer",
         "React, TypeScript, Next.js", "$100–140/hr",
         "jobs@agency.example", "https://news.ycombinator.com/item?id=lead2",
         "Remote-only, US timezones."],
        ["2026-05-05", "Twitter/X", "ML Engineer (RAG)",
         "Python, LangChain, pgvector", "$10k flat (4 weeks)",
         "founder@example.com", "https://x.com/example/status/lead3",
         "Replace with your real lead row."],
    ]
    for r in examples:
        ws.append(r)

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = WRAP

    style_header(ws, len(headers))
    autosize(ws)
    ws.column_dimensions["H"].width = 50

    wb.save(path)


def main():
    buyer = HERE / "buyer_outreach_kit.xlsx"
    leads = HERE / "may2026_freelance_leads.xlsx"

    write_buyer_outreach_kit(buyer)
    write_freelance_leads(leads)

    print(f"Wrote {buyer.name}")
    print(f"Wrote {leads.name}")
    print()
    print("Next steps:")
    print("  1. Open buyer_outreach_kit.xlsx and replace the example rows with your real buyers.")
    print("  2. Find-and-replace [Your name] and [Your contact link] in the Body column.")
    print("  3. Open send_emails.py, set GMAIL_ADDRESS / FROM_NAME (and later GMAIL_APP_PASSWORD).")
    print("  4. Run:  python3 send_emails.py    # dry-run preview")
    print("  5. Flip DRY_RUN = False and run again to send for real.")


if __name__ == "__main__":
    main()
