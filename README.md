# MSP Unified Platform (MVP)

מערכת התחלתית לחברת MSP הכוללת:
- **RMM** לניהול תחנות קצה
- **EDR** לניטור התראות אבטחה
- **Backup** לסטטוס גיבויים
- **Remote Control** ללקוחות קבועים וגם חד-פעמיים
- **PSA** לניהול קריאות שירות
- **Accounting** לסנכרון בנקים והפקת חשבוניות דרך ספק צד-ג' מאושר

## מהו הקובץ Su.exe.exe

הקובץ הוא **SimpleHelp Remote Access Client** — תוכנת צד-שלישי מסחרית (SimpleHelp Ltd) לגישה ושליטה מרחוק, המשמשת כאן כרכיב Remote Control עבור לקוחות ה-MSP. הוא **לא** נכתב כחלק מהפרויקט הזה ואינו קוד פתוח — זהו קובץ בינארי חיצוני שצורף לריפו.

לפני שמריצים אותו על מחשב כלשהו:
- ודאו שקיבלתם אותו ממקור מהימן (חשבון SimpleHelp שלכם / מי שאחראי על הפריסה בארגון).
- אם יש לכם רישיון SimpleHelp פעיל, מומלץ להוריד את הקובץ ישירות מקונסולת ה-SimpleHelp שלכם ולא להסתמך על עותק ישן שיושב בריפו — כך תקבלו גרסה עדכנית וחתומה כראוי.
- בדקו את הרישיון של SimpleHelp לפני הפצת הקובץ הבינארי הזה מחוץ לארגון שלכם — זו תוכנה מסחרית, לא קוד פתוח.

הקובץ נמצא כאן בפרויקט:
- `/workspace/PPL/Su.exe.exe`

ב-Windows זה צריך להיות באותה תיקייה הראשית של הפרויקט (ליד `README.md`).

אם אתה רוצה לוודא בפקודה:
```powershell
Get-ChildItem -Path . -Filter Su.exe.exe -Recurse
```

## איפה מורידים את זה?

כרגע אין לינק הורדה ציבורי בתוך הפרויקט הזה.

יש שתי אפשרויות:
1. אם קיבלת כבר את הקובץ `Su.exe.exe` — **לא צריך להוריד כלום**, פשוט להריץ אותו.
2. אם אין לך את `Su.exe.exe` — צריך לבקש ממי שבנה/מחזיק את המערכת שישלח לך את קובץ ה־EXE או קישור הורדה.

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

> אם Windows SmartScreen חוסם את ההרצה — זו התראת אבטחה לגיטימית, לא תקלה להתעלם ממנה. לפני שממשיכים: ודאו מול המקור (ראו "מהו הקובץ Su.exe.exe" למעלה) שהקובץ אכן הגיע מ-SimpleHelp ולא הוחלף/שונה בדרך. אל תעקפו את ההתראה על קובץ שאינכם בטוחים לגביו.

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
- Health: `http://127.0.0.1:8000/health` (נקודת הקצה היחידה שלא דורשת אימות)

## אימות (Authentication)

כל נקודות הקצה מלבד `/health` דורשות כותרת `X-API-Key`. ברירת המחדל בפיתוח היא `dev-key`; לשינוי הגדירו משתנה סביבה לפני ההרצה:

```powershell
$env:MSP_API_KEY = "my-secret-key"
```

דוגמה לקריאה:
```bash
curl -H "X-API-Key: dev-key" http://127.0.0.1:8000/customers
```

## מסד נתונים

הנתונים נשמרים ב-SQLite, בקובץ `msp.db` שנוצר אוטומטית בתיקיית הפרויקט בהרצה הראשונה (נתוני דמו לדוגמה `cust-1`/`ep-1` מוזרעים אוטומטית אם לא קיימים). לשינוי המיקום או למעבר למסד נתונים אחר (למשל PostgreSQL בפרודקשן), הגדירו את `MSP_DATABASE_URL`:

```powershell
$env:MSP_DATABASE_URL = "postgresql://user:pass@host:5432/msp"
```

## נקודות קצה עיקריות

**לקוחות**
- `GET /customers`
- `POST /customers`

**RMM**
- `GET /rmm/endpoints`
- `POST /rmm/endpoints` — רישום תחנת קצה/agent חדשה
- `POST /rmm/remote-session/{endpoint_id}`
- `POST /rmm/endpoints/{endpoint_id}/heartbeat` — צ'ק-אין תקופתי מה-agent
- `POST /rmm/endpoints/{endpoint_id}/tasks` — הכנסת סקריפט/פקודה לתור
- `GET /rmm/endpoints/{endpoint_id}/tasks` — רשימת המשימות של תחנה
- `POST /rmm/tasks/{task_id}/result` — דיווח תוצאה מה-agent
- `GET /rmm/patches` — סיכום תחנות עם עדכונים ממתינים

**EDR / Backup**
- `GET /edr/alerts`
- `GET /backup/status`

**PSA**
- `POST /psa/tickets` — כולל חישוב SLA (`due_at`) לפי עדיפות
- `GET /psa/tickets` — תמיכה בפילטרים `open_only` ו-`customer_id`
- `GET /psa/tickets/overdue`
- `GET /psa/tickets/{ticket_id}`
- `PATCH /psa/tickets/{ticket_id}` — עדכון סטטוס / אחראי / עדיפות
- `POST /psa/tickets/{ticket_id}/comments`
- `GET /psa/tickets/{ticket_id}/comments`

**Accounting**
- `POST /accounting/banks/sync/{customer_id}`
- `POST /accounting/invoices`

## הערה לארגון Production

זהו MVP בלבד. בפרודקשן מומלץ להוסיף:
- RBAC / SSO (מעבר ל-API key בודד)
- מסד נתונים ניהולי (PostgreSQL) במקום SQLite
- תורים אסינכרוניים למשימות RMM/Backup
- הצפנת סודות ו-KMS
- חיבור אמיתי לספקי בנקאות וחשבוניות מאושרים
