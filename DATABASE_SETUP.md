# Docker Database Configuration Guide

## Why Update settings.py for Docker?

When you dockerize your Django application, you need to make your `settings.py` **flexible** to work in different environments:

- 🏠 **Local Development** - Your computer (SQLite)
- 🐳 **Docker Development** - Docker containers (SQLite or PostgreSQL)
- 🚀 **Docker Production** - Production server (PostgreSQL + Nginx)

## What Changed in settings.py?

### Before (Hardcoded):
```python
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

### After (Environment-based):
```python
DATABASE_ENGINE = config('DATABASE_ENGINE', default='django.db.backends.sqlite3')

if DATABASE_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / config('DATABASE_NAME', default='db.sqlite3'),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DATABASE_ENGINE,
            "NAME": config('DATABASE_NAME', default='django_db'),
            "USER": config('DATABASE_USER', default='django_user'),
            "PASSWORD": config('DATABASE_PASSWORD', default='django_password'),
            "HOST": config('DATABASE_HOST', default='db'),
            "PORT": config('DATABASE_PORT', default='5432'),
        }
    }
```

## Benefits:

✅ **Flexibility** - Switch databases without changing code
✅ **Security** - Credentials in `.env` file, not in code
✅ **Docker-ready** - Uses environment variables from Docker Compose
✅ **Production-safe** - Different settings for dev/prod

## How It Works:

### 1. Environment Variables (`.env` file)

Your `.env` file controls the database:

**For SQLite (Simple Development):**
```env
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

**For PostgreSQL (Production):**
```env
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=django_db
DATABASE_USER=django_user
DATABASE_PASSWORD=django_password
DATABASE_HOST=db
DATABASE_PORT=5432
```

### 2. Docker Compose Sets These Variables

Your `docker-compose.yml` can override `.env`:

```yaml
services:
  web:
    environment:
      - DATABASE_ENGINE=django.db.backends.postgresql
      - DATABASE_NAME=django_db
      - DATABASE_USER=django_user
      - DATABASE_PASSWORD=django_password
      - DATABASE_HOST=db  # ← This is the PostgreSQL service name
      - DATABASE_PORT=5432
```

### 3. Python-decouple Reads Them

```python
from decouple import config

DATABASE_ENGINE = config('DATABASE_ENGINE', default='django.db.backends.sqlite3')
```

## Different Scenarios:

### Scenario 1: Local Development (No Docker)
```bash
# .env file
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Run normally
python manage.py runserver
```

### Scenario 2: Docker Development (SQLite)
```yaml
# docker-compose.yml
services:
  web:
    environment:
      - DATABASE_ENGINE=django.db.backends.sqlite3
      - DATABASE_NAME=db.sqlite3
```

```bash
docker-compose up
```

### Scenario 3: Docker Production (PostgreSQL)
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=django_db
      - POSTGRES_USER=django_user
      - POSTGRES_PASSWORD=django_password
  
  web:
    environment:
      - DATABASE_ENGINE=django.db.backends.postgresql
      - DATABASE_NAME=django_db
      - DATABASE_USER=django_user
      - DATABASE_PASSWORD=django_password
      - DATABASE_HOST=db  # ← Service name
      - DATABASE_PORT=5432
    depends_on:
      - db
```

## Important Notes:

### 🔑 DATABASE_HOST in Docker

When using Docker Compose with PostgreSQL:
- ✅ Use `DATABASE_HOST=db` (the service name)
- ❌ NOT `127.0.0.1` or `localhost`

**Why?** Docker Compose creates a network where services communicate by service name.

### 📁 Current Setup

Your current `docker-compose.yml` uses **SQLite**, so:
- Database file is stored in a Docker volume: `db_volume:/app/db`
- No separate PostgreSQL container
- Simple and fast for development

### 🔄 To Switch to PostgreSQL

Update your `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=django_db
      - POSTGRES_USER=django_user
      - POSTGRES_PASSWORD=django_password
    ports:
      - "5432:5432"
  
  web:
    depends_on:
      - db
    environment:
      - DATABASE_ENGINE=django.db.backends.postgresql
      - DATABASE_NAME=django_db
      - DATABASE_USER=django_user
      - DATABASE_PASSWORD=django_password
      - DATABASE_HOST=db
      - DATABASE_PORT=5432

volumes:
  postgres_data:
```

## Testing Your Setup

### Check Current Database Config:
```bash
docker-compose exec web python manage.py shell

# In Django shell:
from django.conf import settings
print(settings.DATABASES)
```

### Run Migrations:
```bash
docker-compose exec web python manage.py migrate
```

### Create Test Data:
```bash
docker-compose exec web python manage.py seed
```

## Common Issues:

### Issue 1: "No module named 'psycopg2'"
**Solution:** Already fixed! We added `psycopg2-binary` to `requirements.txt`

### Issue 2: "Connection refused to database"
**Check:**
- Is PostgreSQL container running? `docker-compose ps`
- Is `DATABASE_HOST=db` (not `localhost`)?
- Did database start before web service? Use `depends_on`

### Issue 3: "Database 'django_db' does not exist"
**Solution:** PostgreSQL container creates it automatically from `POSTGRES_DB` env var

## Summary:

| Environment | Database | Configuration |
|------------|----------|---------------|
| Local Dev | SQLite | `.env` file |
| Docker Dev | SQLite | `docker-compose.yml` env vars |
| Docker Prod | PostgreSQL | `docker-compose.yml` + separate DB service |

**Your current setup:** ✅ Docker with SQLite (simple and works!)

**To upgrade:** Add PostgreSQL service to `docker-compose.yml` and update env vars.

## Quick Reference:

```bash
# View current database settings
docker-compose exec web python -c "from django.conf import settings; print(settings.DATABASES)"

# Check what environment variables are set
docker-compose exec web env | grep DATABASE

# Test database connection
docker-compose exec web python manage.py dbshell
```

---

**Bottom Line:** Yes, you need to update `settings.py` for Docker, and we just did that! ✅ Now your app can work with both SQLite (current) and PostgreSQL (future) just by changing environment variables.
