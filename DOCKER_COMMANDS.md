# 🐳 Docker Commands - Quick Reference

## 🚀 First Time Setup

### 1. Build the Docker Image
```powershell
docker-compose build
```
**What this does:** Creates a Docker image with Python, your dependencies, and your code.

### 2. Start the Application
```powershell
docker-compose up
```
**What this does:**
- Runs migrations (`python manage.py migrate`)
- Seeds the database (`python manage.py seed`)
- Starts Django dev server on `http://localhost:8000`

**Run in background (detached mode):**
```powershell
docker-compose up -d
```

---

## 🔄 Daily Development Workflow

### Start the app
```powershell
docker-compose up
```

### Stop the app (keeps containers)
```powershell
# Press Ctrl+C in the terminal where it's running
# OR if running in detached mode:
docker-compose stop
```

### Stop and remove containers
```powershell
docker-compose down
```

### View logs (if running in background)
```powershell
docker-compose logs -f web
```

---

## 🔨 When You Make Changes

### Code changes (Python files)
**No rebuild needed!** The code is mounted, so changes appear immediately.
Just refresh your browser or restart the server:
```powershell
docker-compose restart web
```

### Added a new Python package
**Rebuild required:**
```powershell
# 1. Add package to requirements.txt
# 2. Rebuild
docker-compose build web

# 3. Restart
docker-compose up -d
```

### Changed Dockerfile
**Rebuild required:**
```powershell
docker-compose build --no-cache
docker-compose up -d
```

### Changed docker-compose.yml
**No rebuild, just restart:**
```powershell
docker-compose down
docker-compose up -d
```

---

## 🛠️ Useful Commands

### Run Django management commands
```powershell
# General format
docker-compose exec web python manage.py <command>

# Examples:
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py seed
docker-compose exec web python manage.py shell
```

### Access container shell
```powershell
docker-compose exec web bash
```

### Check running containers
```powershell
docker-compose ps
```

### View logs
```powershell
# All logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

### Restart service
```powershell
docker-compose restart web
```

---

## 🗑️ Clean Up

### Remove containers (keeps images)
```powershell
docker-compose down
```

### Remove containers and volumes (fresh start)
```powershell
docker-compose down -v
```

### Remove everything including images
```powershell
docker-compose down --rmi all -v
```

---

## 🎯 Common Scenarios

### Fresh start (clean database)
```powershell
docker-compose down -v
docker-compose up -d
```

### Re-seed database
```powershell
docker-compose exec web python manage.py flush --noinput
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed
```

### Install new package
```powershell
# 1. Add to requirements.txt
# 2. Rebuild
docker-compose build web
docker-compose up -d
```

### Check if app is running
```powershell
docker-compose ps
# OR visit: http://localhost:8000
```

---

## 📊 What's Fixed

✅ **Volume mount:** Now correctly mounts `.` to `/app` (matches Dockerfile WORKDIR)
✅ **Database:** Runs `migrate` instead of `flush` (won't wipe data every time)
✅ **Seeding:** Seeds only once when database is empty
✅ **Live reload:** Code changes reflect immediately (volume mount)

---

## 🎬 Complete Workflow Example

```powershell
# First time
docker-compose build
docker-compose up -d

# Check it's running
docker-compose ps
docker-compose logs -f web

# Make code changes (automatically picked up)
# Edit your Python files...

# Add a new package
# 1. Add to requirements.txt
# 2. Rebuild:
docker-compose build web
docker-compose up -d

# Stop when done
docker-compose down
```

---

## ⚠️ Troubleshooting

### Port already in use
```powershell
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Container won't start
```powershell
# Check logs
docker-compose logs web

# Try clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Database issues
```powershell
# Fresh database
docker-compose down -v
docker-compose up -d
```

---

## 📝 Access Your App

- **API:** http://localhost:8000/api/
- **Admin:** http://localhost:8000/cms/
- **Home Hero Section:** http://localhost:8000/api/home-page-hero-section/

---

**Need help?** Check the logs: `docker-compose logs -f web`
