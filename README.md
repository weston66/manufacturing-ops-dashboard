# manufacturing-ops-dashboard

Real-time manufacturing operations dashboard that surfaces work order status, inventory health, and vendor performance in one view - with automated Slack alerts when things go wrong.

---

## Architecture

```
PostgreSQL DB
  ├── work_orders
  ├── inventory
  └── vendors
       │
       ▼
    db.py (psycopg2 / RealDictCursor)
       │
       ▼
    app.py (Streamlit)
  ├── KPI tiles (open WOs, overdue, completion rate, low stock, vendor on-time)
  ├── Plotly charts (status/priority breakdown, stock levels, vendor rates)
  └── alerts.py ──► Slack Webhook
```

---

## Tech Stack

- Python 3.11
- Streamlit - dashboard UI
- PostgreSQL - operational data store
- psycopg2 - database driver
- Plotly Express - charting
- pandas - data transformation
- Slack Webhooks - alerting
- python-dotenv - environment config

---

## What Problem It Solves

Manufacturing floors run on work orders. When those slip, everything downstream slips - assembly, shipping, customer commitments. The problem is that the data to catch these slips usually lives in an ERP, buried behind reports nobody pulls until it's too late.

This dashboard pulls work order status, inventory reorder levels, and vendor on-time rates into a single live view. Overdue orders and low-stock parts trigger Slack alerts automatically on page load, so the ops team gets notified without having to go looking. Designed for environments where production supervisors need signal, not spreadsheets.

---

## How to Run It Locally

**Prerequisites:** Python 3.11+, PostgreSQL running locally or via Docker

**1. Clone the repo**
```bash
git clone https://github.com/weston66/manufacturing-ops-dashboard.git
cd manufacturing-ops-dashboard
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**

Create a `.env` file in the root:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASS=your_db_password
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

**4. Set up the database**

Create the required tables in your PostgreSQL instance:
```sql
CREATE TABLE work_orders (
    status TEXT,
    priority TEXT,
    qty_ordered INT,
    qty_completed INT,
    due_date DATE
);

CREATE TABLE inventory (
    part_number TEXT,
    description TEXT,
    on_hand_qty INT,
    reorder_point INT,
    unit_cost NUMERIC
);

CREATE TABLE vendors (
    vendor_name TEXT,
    on_time_rate NUMERIC,
    lead_time_days INT
);
```

**5. Run the dashboard**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Screenshots / Demo

_Screenshots pending. Dashboard includes:_

- _Five KPI tiles: open work orders, overdue count, completion rate, low stock parts, average vendor on-time rate_
- _Work order breakdown by status and priority (bar charts)_
- _Inventory on-hand vs. reorder point by part number_
- _Vendor on-time rate comparison_
- _Manual Slack alert trigger button_
