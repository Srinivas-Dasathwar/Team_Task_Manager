<<<<<<< HEAD
# Team Task Manager

## Railway Deployment Guide

This Django app is ready for deployment to Railway.

### 1. Ensure required files exist
- `requirements.txt`
- `Procfile`
- `runtime.txt`
- `team_task_manager/settings.py`

### 2. Set Railway environment variables
In Railway settings, add:
- `DJANGO_SECRET_KEY` — a secure secret value
- `DATABASE_URL` — automatically created when adding a PostgreSQL plugin
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=<your-railway-app-domain>`

### 3. Railway deployment steps
1. Create a new project on Railway.
2. Connect your GitHub repository or upload this project.
3. Add the PostgreSQL plugin.
4. Railway will detect the `Procfile` and install dependencies from `requirements.txt`.
5. Add the environment variables.
6. Deploy.

### 4. Required commands after deployment or locally
- `python manage.py migrate`
- `python manage.py collectstatic --noinput`

### 5. Local setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

### 6. Railway specific notes
- `Procfile` uses: `web: gunicorn team_task_manager.wsgi --log-file -`
- `whitenoise` serves static files in production
- `DATABASE_URL` is used automatically when available

### 7. Useful URLs
- Local: `http://127.0.0.1:8000/`
- API docs: use your app root plus endpoints like `/api/projects/`
=======
# Team_Task_Manager
>>>>>>> 4eee3f539987c65d6cc58b659e0911d23feb1006
