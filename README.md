# eTeydeb Project Analyzer

A lightweight Python utility that periodically retrieves your project list from the **TÜBİTAK e-Teydeb** portal and tracks changes over time.  
It’s built to deliver operational visibility (a.k.a. “stop clicking the portal 20 times a day”) by detecting updates such as **project status transitions**, **commercialization status changes**, and **TEYDEB manager** updates, then persisting a clean “current snapshot” in MongoDB with optional change history.

---

## What it does

- Polls the e‑Teydeb project list on a configurable interval
- Parses HTML into structured project metadata (code, name, support type, application date, owner, status, commercialization status, manager)
- Detects changes (field-level deltas) and logs them
- Persists results in MongoDB:
  - **Current state** per `project_code` (upsert)
  - Optional `status_history` array for auditability

---

## Tech stack

- Python 3.10+ (works on 3.8+ in most cases, but modern is better)
- `requests` + `BeautifulSoup` (HTML parsing)
- MongoDB + `pymongo` (storage)

---

## Repository structure (suggested)

```
.
├── eteydeb_analyzer.py
├── cookies.txt              # NOT committed
├── README.md
└── requirements.txt
```

---

## Prerequisites

- A working **MongoDB** instance (local or remote)
- A valid **e‑Teydeb session cookie** exported/saved to a local text file (see below)
- Network access to the e‑Teydeb portal

---

## Installation

### 1) Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -U pip
pip install requests beautifulsoup4 lxml pymongo
```

Optional (nice-to-have):

```bash
pip install python-dotenv
```

---

## Configuration

### Cookies file (simple text)

Create `cookies.txt` (do not commit it). Supported formats:

**Format A: `name=value` per line**
```
sessionid=YOUR_VALUE
csrftoken=YOUR_VALUE
```

**Format B: full cookie header on one line**
```
sessionid=YOUR_VALUE; csrftoken=YOUR_VALUE; theme=dark
```

> **Security note:** This cookie is effectively a credential. Treat it like a password:
> - keep it out of source control (`.gitignore`)
> - don’t paste it into tickets/slack
> - rotate it when needed

### MongoDB settings

Default:
- URI: `mongodb://localhost:27017`
- DB: `teydeb`
- Collection: `projects`

Adjust in code (or convert to env vars if you prefer grown-up deployments).

---

## Usage

Run the polling loop:

```bash
python eteydeb_analyzer.py
```

You should see periodic log lines like:

- Polling timestamp
- “Project X changed” when a tracked field changes

Stop with `CTRL+C`.

---

## Data model (MongoDB)

Each document is keyed by `project_code` and represents the latest known snapshot:

```json
{
  "project_code": 123456,
  "project_name": "…",
  "support_type": "…",
  "project_type": "…",
  "application_date": "…",
  "project_owner": "…",
  "project_status": "…",
  "project_commercialization_status": "…",
  "teydeb_manager": "…",
  "created_at": "2026-01-08T07:00:00Z",
  "updated_at": "2026-01-08T07:05:00Z",
  "status_history": [
    {
      "ts": "2026-01-08T07:05:00Z",
      "changes": {
        "project_status": { "from": "…", "to": "…" }
      }
    }
  ]
}
```

Indexes:
- `project_code` should be **unique** for safe upserts and performance.

---

## Troubleshooting

### 1) You keep getting HTML that looks like a login page
Your cookie is likely expired or incomplete.
- Re-login in browser
- Re-export the cookie
- Make sure you’re hitting the same domain and path constraints

### 2) Parser returns zero projects
The portal HTML may have changed, or you’re not authenticated.
- Inspect `response.status_code` and `Content-Type`
- Print a snippet of the HTML and confirm `table.veriListeTablo` exists

### 3) HTTP 403 / 302 redirects
- Cookie invalid/expired
- Portal requires additional headers or a fresh session

### 4) Mongo errors
- Confirm MongoDB is running and accessible
- Check URI / credentials / firewall

---

## Roadmap (optional but realistic)

- Alerting integration (email/Slack/webhook)
- Persist raw HTML snapshots for forensic debugging
- Docker support (containerized polling + Mongo)
- OAuth/session automation (if the portal flow allows it)
- Dashboard layer (Grafana/Metabase) for reporting

---

## Contributing

PRs welcome:
- Keep parsing robust (defensive selectors)
- Keep secrets out of code and out of commits
- Add tests for HTML parsing (fixtures help)

---

## License

Add a license that matches your organization’s compliance posture (MIT/Apache-2.0 are common choices).
