# MSP Unified Platform (MVP)

מערכת התחלתית לחברת MSP הכוללת:
- **RMM** לניהול תחנות קצה
- **EDR** לניטור התראות אבטחה
- **Backup** לסטטוס גיבויים
- **Remote Control** ללקוחות קבועים וגם חד-פעמיים
- **PSA** לניהול קריאות שירות
- **Accounting** לסנכרון בנקים והפקת חשבוניות דרך ספק צד-ג' מאושר

## הרצה

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## נקודות קצה עיקריות

- `GET /rmm/endpoints`
- `POST /rmm/remote-session/{endpoint_id}`
- `GET /edr/alerts`
- `GET /backup/status`
- `POST /psa/tickets`
- `POST /accounting/banks/sync/{customer_id}`
- `POST /accounting/invoices`

## הערה לארגון Production

זהו MVP בלבד. בפרודקשן מומלץ להוסיף:
- RBAC / SSO
- מסד נתונים (PostgreSQL)
- תורים אסינכרוניים למשימות RMM/Backup
- הצפנת סודות ו-KMS
- חיבור אמיתי לספקי בנקאות וחשבוניות מאושרים
