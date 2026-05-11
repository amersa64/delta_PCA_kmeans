# Quickstart — auto-send 46 buyer emails

End-to-end: ~20 minutes of laptop time.

You have four files in this folder:

| File | Purpose |
|---|---|
| `send_emails.py` | Reads the XLSX and sends every row that has an email. Dry-run by default. Resumable. |
| `make_templates.py` | One-shot script that re-generates the two XLSX templates if you need to start over. |
| `buyer_outreach_kit.xlsx` | Buyer list + pre-written personalized emails. **Replace example rows with your real 46 buyers.** |
| `may2026_freelance_leads.xlsx` | The deliverable you email to buyers after they pay. |

---

## Path A — Let Claude Code drive (recommended)

In your terminal:

```bash
cd /path/to/this/folder
claude
```

Paste this prompt:

> I have `buyer_outreach_kit.xlsx` and `send_emails.py` in this folder. Walk
> me through: setting up a Gmail App Password, editing the script config with
> my email and name, doing find-and-replace for `[Your name]` and
> `[Your contact link]` in the XLSX, running dry-run, then sending live.
> My Gmail is `<you@gmail.com>`, name is `<Your Name>`, contact link is
> `<https://your-link>`.

Claude Code will:
1. Open the Gmail App Password page for you (you copy the 16-char code back).
2. Edit `send_emails.py` config block — `GMAIL_ADDRESS`, `FROM_NAME`, `GMAIL_APP_PASSWORD`.
3. Find-and-replace `[Your name]` and `[Your contact link]` across the XLSX.
4. Run `python3 send_emails.py` (still in dry-run) so you can review three sample emails.
5. Flip `DRY_RUN = False` and re-run when you approve.

You review and approve. That's it.

---

## Path B — Plain Python (no Claude Code)

### 1. Install the one dependency

```bash
pip install -r requirements.txt
```

### 2. Get a Gmail App Password (5 min)

1. Turn on 2-Step Verification: <https://myaccount.google.com/signinoptions/twosv>
2. Create an App Password: <https://myaccount.google.com/apppasswords>
   - App: "Mail", Device: "Other (Custom)" → name it "send_emails"
   - Copy the 16-character password. **Spaces don't matter — strip them.**

### 3. Edit your real data into the XLSX

Open `buyer_outreach_kit.xlsx`:

- Replace the example rows with your 46 buyers.
- Columns: `Name`, `Email`, `Source`, `Link`, `Subject`, `Body`, `Notes`.
- **Rows with an empty `Email` are skipped** by the script — handle those buyers manually via DM.
- Do a single find-and-replace pass on the whole sheet:
  - `[Your name]` → your name
  - `[Your contact link]` → e.g. `https://cal.com/you` or your portfolio URL
- Save.

### 4. Configure the script

Open `send_emails.py`. Edit the config block near the top:

```python
GMAIL_ADDRESS      = "you@gmail.com"
GMAIL_APP_PASSWORD = "abcdabcdabcdabcd"   # 16 chars, no spaces
FROM_NAME          = "Your Name"
```

Leave `DRY_RUN = True` for now.

### 5. Dry-run

```bash
python3 send_emails.py
```

You'll see:

```
Total rows        : 46
With email        : 36  (auto-sendable)
Link-only (manual): 10
Already sent      : 0
To send this run  : 36
Mode              : DRY-RUN (no emails sent)
```

Plus three rendered preview emails. If anything looks wrong, fix the XLSX and re-run.

If the script warns about leftover `[Your name]` / `[Your contact link]` placeholders, redo find-and-replace.

### 6. Send for real

Edit `send_emails.py`:

```python
DRY_RUN = False
```

Run it:

```bash
python3 send_emails.py
```

The script will:
- Connect to Gmail SMTP over SSL.
- Send each email with a 25-second pause between sends (Gmail rate-limit friendly).
- Log every attempt to `send_log.csv` (timestamp, email, status, note).
- Skip any address already marked `sent` in the log if you re-run.

Total wall time: ~15 minutes for 36 emails.

### 7. Triage replies

This is the only part Claude Code can't do for you. Budget 60–90 minutes:
- Reply fast to interested buyers.
- Send Stripe link.
- Email `may2026_freelance_leads.xlsx` when payment clears.

---

## If something goes wrong

| Symptom | Fix |
|---|---|
| `smtplib.SMTPAuthenticationError` | Wrong App Password, or 2FA isn't on. Regenerate the App Password and paste fresh. |
| Script halts mid-send (Ctrl-C, crash, laptop closed) | Just re-run. `send_log.csv` tracks who's been sent — already-sent emails are skipped. |
| You want to start over with fresh emails | Delete `send_log.csv`. |
| Want to regenerate the XLSX templates | `python3 make_templates.py` (this overwrites both XLSX files — back them up first if you've added real data). |
| Edited an email and want to re-send | Delete that row's entry from `send_log.csv`, then re-run. |

---

## Realistic outcome

- **15 min** auto-send to 36 buyers with direct email.
- **10 link-only** buyers — DM manually if you want; same template, paste into Reddit/HN reply.
- **3–6 sales × $49 = $147–$294** is the realistic zone.
- The automation frees you to focus on the high-leverage part: replying fast to interested buyers.
