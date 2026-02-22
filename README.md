# MSP Unified Platform (MVP)

מערכת התחלתית לחברת MSP הכוללת:
- **RMM** לניהול תחנות קצה
- **EDR** לניטור התראות אבטחה
- **Backup** לסטטוס גיבויים
- **Remote Control** ללקוחות קבועים וגם חד-פעמיים
- **PSA** לניהול קריאות שירות
- **Accounting** לסנכרון בנקים והפקת חשבוניות דרך ספק צד-ג' מאושר

## איך מורידים ומריצים על Windows

### דרישות מוקדמות
1. התקן **Python 3.11 ומעלה** (סמן בזמן התקנה: "Add python.exe to PATH").
2. פתח PowerShell בתיקיית הפרויקט.

### אפשרות מהירה (מומלץ)
```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_windows.ps1 -Dev
```

או בלחיצה כפולה על:
```text
scripts\start_windows.bat
```

הסקריפט:
- יוצר `.venv`
- מתקין תלויות
- מרים את השרת על `http://127.0.0.1:8000`

### אפשרות ידנית
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
uvicorn app.main:app --reload
```

### בדיקה שהמערכת עלתה
פתח בדפדפן:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

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
