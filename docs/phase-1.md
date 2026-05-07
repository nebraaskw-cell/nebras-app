# Phase 1

Implemented:

- Project setup with Django and DRF.
- `accounts.User` custom user model.
- Roles: admin, student, teacher, parent, visitor.
- Student registration status: pending, approved, rejected.
- Student registration web form and API endpoint.
- Admin approval action for pending students.
- Permanent `Circle` model.
- Three-month `Cycle` model with default 4 PM - 6 PM session window.
- Admin configuration for users, circles, and cycles.
- Basic template views.
- API routers for circles and cycles.

Run:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

