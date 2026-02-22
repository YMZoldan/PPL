# MSP Unified Platform (MVP)

מערכת התחלתית לחברת MSP הכוללת:
- **RMM** לניהול תחנות קצה
- **EDR** לניטור התראות אבטחה
- **Backup** לסטטוס גיבויים
- **Remote Control** ללקוחות קבועים וגם חד-פעמיים
- **PSA** לניהול קריאות שירות
- **Accounting** לסנכרון בנקים והפקת חשבוניות דרך ספק צד-ג' מאושר

## אין לך מה להוריד? הפעלה ישירה על Windows (ללא התקנה)

אם כבר יש לך את הקובץ `Su.exe.exe`, אפשר להפעיל בלי Python ובלי התקנות נוספות:

### אפשרות 1: לחיצה כפולה
- לחץ פעמיים על `Su.exe.exe`.

### אפשרות 2: דרך סקריפט עזר
- לחץ פעמיים על `scripts\run_portable_windows.bat`
- או הרץ ב-CMD מתוך תיקיית הפרויקט:
```bat
scripts\run_portable_windows.bat
```

> אם Windows SmartScreen חוסם: לחץ "More info" ואז "Run anyway" (רק אם אתה סומך על הקובץ).

## הרצה עם קוד המקור (למי שכן רוצה לפתח)

### דרישות מוקדמות
1. התקן **Python 3.11 ומעלה** (סמן בזמן התקנה: "Add python.exe to PATH").
2. פתח PowerShell בתיקיית הפרויקט.

### אפשרות מהירה
```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_windows.ps1 -Dev
```

או בלחיצה כפולה על:
```text
scripts\start_windows.bat
```

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
