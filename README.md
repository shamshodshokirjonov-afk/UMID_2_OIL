# UMID 2 OIL

Django-based website for the UMID 2 OIL fuel station.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sign in at `/login/` to view the site. Manage fuel prices and daily station
statistics at `/admin/`. The public statistics table summarizes the daily
entries for today, the current week, the current month, and the current year.