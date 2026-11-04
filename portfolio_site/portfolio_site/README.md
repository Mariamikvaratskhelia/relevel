# ReLevel – Level up your future in Germany

ReLevel helps international students plan their path to studying in Germany.

## Technology

Stack: Django, Django REST Framework, SimpleJWT, PostgreSQL, Redis, Celery, drf-spectacular (Swagger), Docker, Git.

## Run
    cp .env.example .env
    docker compose up --build
    docker compose exec web python manage.py migrate
    docker compose exec web python manage.py createsuperuser

- Website:      http://localhost:8000/
- Dashboard:    http://localhost:8000/dashboard/
- Admin:        http://localhost:8000/admin/
- Swagger UI:   http://localhost:8000/api/docs/

### Email setup
Set real SMTP values in `.env` before starting Docker:

    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=1
    EMAIL_HOST_USER=your-email@example.com
    EMAIL_HOST_PASSWORD=your-app-password
    DEFAULT_FROM_EMAIL=your-email@example.com
    CONTACT_RECIPIENT=your-email@example.com

If you leave these blank, the project falls back to the console email backend for local development.

## Auth
    POST /api/token/          {"username": "...", "password": "..."}  -> access + refresh
    POST /api/token/refresh/  {"refresh": "..."}
Send `Authorization: Bearer <access>` for write requests (POST/PUT/DELETE on projects and skills).

## Git
    git init && git add . && git commit -m "Initial commit"
