# EduGuard Render Deployment

## Recommended Settings

Use Render Web Service for the Flask app.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn wsgi:app --workers 1 --timeout 120
```

Environment variables:

```text
FLASK_CONFIG=production
SECRET_KEY=<generate-a-long-random-secret>
DATABASE_URL=<optional-postgres-internal-url>
```

If you skip `DATABASE_URL`, the app uses SQLite. That is fine for a demo, but hosted SQLite can reset on some platforms. For a more reliable deployment, create a Postgres database and set `DATABASE_URL` to its internal URL.

## Login After Deploy

Admin:

```text
admin@eduguard.edu
admin123
```

Student:

```text
john.doe@eduguard.edu
student123
```
