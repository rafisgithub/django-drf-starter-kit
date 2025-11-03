# How to Switch from SQLite to PostgreSQL

You have **2 options** to switch databases:

---

## Option 1: Using .env File (Simple)

### Current Setup (SQLite):
Your `.env` file currently has:
```env
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

### To Switch to PostgreSQL:

1. **Update your `.env` file**:
   ```env
   # Comment out SQLite
   # DATABASE_ENGINE=django.db.backends.sqlite3
   # DATABASE_NAME=db.sqlite3

   # Uncomment PostgreSQL
   DATABASE_ENGINE=django.db.backends.postgresql
   DATABASE_NAME=django_db
   DATABASE_USER=django_user
   DATABASE_PASSWORD=django_password
   DATABASE_HOST=db
   DATABASE_PORT=5432
   ```

2. **Update `docker-compose.yml`** to include PostgreSQL service:
   ```bash
   # Use the PostgreSQL version
   Copy-Item docker-compose.postgres.yml docker-compose.yml
   ```

3. **Restart Docker**:
   ```bash
   docker-compose down -v
   docker-compose up --build -d
   ```

---

## Option 2: Using Different Docker Compose Files (Recommended)

Keep both configurations and switch between them:

### For SQLite (Development):
```bash
docker-compose up -d
```

### For PostgreSQL (Production-like):
```bash
docker-compose -f docker-compose.postgres.yml up -d
```

---

## Quick Switch Commands:

### Switch to PostgreSQL:
```powershell
# Stop current containers
docker-compose down

# Start with PostgreSQL
docker-compose -f docker-compose.postgres.yml up --build -d

# Check logs
docker-compose -f docker-compose.postgres.yml logs -f
```

### Switch back to SQLite:
```powershell
# Stop PostgreSQL containers
docker-compose -f docker-compose.postgres.yml down

# Start with SQLite
docker-compose up --build -d
```

---

## What's the Difference?

### SQLite (Current - `docker-compose.yml`):
✅ Simple, single file database
✅ Faster startup
✅ No separate database container
✅ Good for development
❌ Not recommended for production
❌ Limited concurrent access

### PostgreSQL (`docker-compose.postgres.yml`):
✅ Production-grade database
✅ Better performance with large data
✅ Supports concurrent users
✅ More features (triggers, views, etc.)
❌ Requires separate container
❌ Slightly slower startup

---

## Step-by-Step: Switching to PostgreSQL Right Now

### 1. Stop current containers:
```powershell
docker-compose down
```

### 2. Start with PostgreSQL:
```powershell
docker-compose -f docker-compose.postgres.yml up --build -d
```

### 3. Wait for database to be ready (about 10-15 seconds):
```powershell
docker-compose -f docker-compose.postgres.yml logs -f
```

### 4. Verify it's working:
```powershell
# Check if both containers are running
docker-compose -f docker-compose.postgres.yml ps

# You should see:
# - django-postgres-db (PostgreSQL)
# - django-web (Django)
```

### 5. Access your app:
```
http://localhost:8000
```

---

## Checking Which Database You're Using

Run this command to see your current database configuration:

```powershell
docker-compose exec web python -c "from django.conf import settings; import json; print(json.dumps(settings.DATABASES, indent=2, default=str))"
```

**SQLite output:**
```json
{
  "default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": "/app/db.sqlite3"
  }
}
```

**PostgreSQL output:**
```json
{
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "django_db",
    "USER": "django_user",
    "HOST": "db",
    "PORT": "5432"
  }
}
```

---

## Migrating Data from SQLite to PostgreSQL

If you want to keep your existing data:

### 1. Export data from SQLite:
```powershell
docker-compose exec web python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > backup.json
```

### 2. Switch to PostgreSQL:
```powershell
docker-compose down
docker-compose -f docker-compose.postgres.yml up -d
```

### 3. Wait for migrations to complete, then import:
```powershell
docker-compose -f docker-compose.postgres.yml exec web python manage.py loaddata backup.json
```

---

## Helper Scripts

Create these batch files for quick switching:

### `start-sqlite.bat`:
```batch
@echo off
docker-compose down
docker-compose up -d
echo SQLite version running on http://localhost:8000
```

### `start-postgres.bat`:
```batch
@echo off
docker-compose -f docker-compose.postgres.yml down
docker-compose -f docker-compose.postgres.yml up -d
echo PostgreSQL version running on http://localhost:8000
```

---

## Environment Variables Priority

The order of precedence (highest to lowest):

1. **Docker Compose `environment:` section** (in .yml file)
2. **`.env` file** (in project root)
3. **`config()` defaults** (in settings.py)

So if you set `DATABASE_ENGINE` in both `.env` and `docker-compose.yml`, the `docker-compose.yml` value wins!

---

## Troubleshooting

### "Connection refused" error:
- Wait 10-15 seconds for PostgreSQL to fully start
- Check: `docker-compose -f docker-compose.postgres.yml logs db`

### "Database does not exist":
- PostgreSQL creates it automatically from `POSTGRES_DB` env var
- Make sure `POSTGRES_DB` matches `DATABASE_NAME`

### Port 5432 already in use:
- Another PostgreSQL instance is running
- Stop it or change port in docker-compose.postgres.yml

---

## Recommendation

For **development**: Use SQLite (current setup)
For **production testing**: Use PostgreSQL (docker-compose.postgres.yml)
For **real production**: Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)

---

**Want to switch now?** Just run:
```powershell
docker-compose -f docker-compose.postgres.yml up -d
```
