# 📦 Dockerfile Explained

## 🔍 Line-by-Line Breakdown

### Current Dockerfile (Development)

```dockerfile
# Use Python 3.13 slim image
FROM python:3.13-slim
```
**What it does:** Downloads a lightweight Python 3.13 image (~120MB vs ~1GB for full version)

---

```dockerfile
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
```
**What it does:**
- `PYTHONDONTWRITEBYTECODE=1` - Don't create `.pyc` files (saves space)
- `PYTHONUNBUFFERED=1` - See Python output in real-time (important for logs)
- `PIP_NO_CACHE_DIR=1` - Don't cache pip downloads (saves space)
- `PIP_DISABLE_PIP_VERSION_CHECK=1` - Skip pip version check (faster builds)

---

```dockerfile
WORKDIR /app
```
**What it does:** Sets `/app` as the working directory inside the container. All subsequent commands run from here.

---

```dockerfile
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```
**What it does:**
- `gcc` - C compiler (needed by some Python packages like Pillow)
- `postgresql-client` - PostgreSQL CLI tools
- `libpq-dev` - PostgreSQL development libraries (for psycopg2)
- `rm -rf /var/lib/apt/lists/*` - Clean up to reduce image size

**Why needed:** Some Python packages have C extensions that need compilation

---

```dockerfile
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
**What it does:**
- Copies `requirements.txt` to `/app/`
- Installs all Python packages

**Why separate layer:** Docker caches this layer. If you change code but not requirements.txt, it won't reinstall packages (faster builds!)

---

```dockerfile
# Copy project files
COPY . .
```
**What it does:** Copies your entire project to `/app/` in the container

**Note:** Files in `.dockerignore` are excluded (like `venv/`, `__pycache__/`)

---

```dockerfile
# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media
```
**What it does:** Creates folders for static files (CSS/JS) and media files (uploads)

---

```dockerfile
EXPOSE 8000
```
**What it does:** Documents that the container listens on port 8000

**Note:** This is just documentation! The actual port mapping is in `docker-compose.yml`

---

```dockerfile
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```
**What it does:** The default command when container starts

**0.0.0.0:8000 means:** Listen on all network interfaces (not just localhost)

---

## 🎯 Improvements Made

### Before:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000
```

### After (Development):
✅ Added environment variables for better Python behavior  
✅ Added system dependencies (gcc, postgresql)  
✅ Created static/media directories  
✅ Better CMD format (exec form vs shell form)  
✅ Added cleanup to reduce image size  

---

## 🏭 Production vs Development

### Development (Current Dockerfile)
- Uses `runserver` (Django dev server)
- ✅ Auto-reload on code changes
- ✅ Better error messages
- ❌ Single-threaded
- ❌ Not secure for production
- ❌ Runs as root user

### Production (Dockerfile.prod)
- Uses `gunicorn` (WSGI server)
- ✅ Multi-threaded (3 workers)
- ✅ Better performance
- ✅ Runs as non-root user (more secure)
- ✅ Multi-stage build (smaller image)
- ✅ Health check included
- ❌ No auto-reload

---

## 📊 Docker Build Process

When you run `docker-compose build`, Docker:

```
1. Downloads python:3.13-slim base image
   └─ Size: ~120MB

2. Sets environment variables
   └─ No size change

3. Sets WORKDIR to /app
   └─ No size change

4. Installs system packages (gcc, postgresql)
   └─ Adds ~100MB (then cleaned up to ~50MB)

5. Copies requirements.txt
   └─ Adds ~1KB

6. Installs Python packages
   └─ Adds ~200MB (your dependencies)

7. Copies project files
   └─ Adds ~10MB (your code)

8. Creates directories
   └─ No significant size change

Final Image Size: ~380MB
```

---

## 🔄 Layer Caching

Docker caches each layer. If nothing changes, it reuses the cache:

```
Step 1: FROM python:3.13-slim
  → Cached ✅ (unless base image updated)

Step 2: ENV variables
  → Cached ✅ (never changes)

Step 3: Install system packages
  → Cached ✅ (rarely changes)

Step 4: COPY requirements.txt
  → Cached ✅ (only changes when you add packages)

Step 5: RUN pip install
  → Cached ✅ (only runs if requirements.txt changed)

Step 6: COPY . .
  → Not cached ❌ (runs every time you change code)
```

**This is why builds are faster after the first time!**

---

## 🚀 Build Commands

### Standard build
```powershell
docker-compose build
```

### Force rebuild (ignore cache)
```powershell
docker-compose build --no-cache
```

### Build production image
```powershell
docker build -f Dockerfile.prod -t django-drf-starter-kit:prod .
```

### Check image size
```powershell
docker images django-drf-starter-kit
```

---

## 🔍 Inspect Your Image

### See layers
```powershell
docker history django-drf-starter-kit-web
```

### Enter running container
```powershell
docker-compose exec web bash
```

### Check installed packages
```powershell
docker-compose exec web pip list
```

### Check Python version
```powershell
docker-compose exec web python --version
```

---

## ⚡ Performance Tips

### 1. Order matters!
Put things that change less often at the top:
- ✅ Base image
- ✅ System packages
- ✅ Python packages (requirements.txt)
- ❌ Your code (changes frequently)

### 2. Use .dockerignore
Exclude unnecessary files:
```
venv/
__pycache__/
*.pyc
.git/
.env
db.sqlite3
```

### 3. Multi-stage builds (production)
Build dependencies in one stage, copy only what's needed to runtime stage.

### 4. Combine RUN commands
```dockerfile
# ❌ Multiple layers
RUN apt-get update
RUN apt-get install -y gcc
RUN rm -rf /var/lib/apt/lists/*

# ✅ One layer
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*
```

---

## 🐛 Common Issues

### Issue: "Package needs compilation but gcc is missing"
**Solution:** System dependencies are now installed (gcc, etc.)

### Issue: "Can't write to /app/"
**Solution:** Volume mount in docker-compose.yml overrides container files

### Issue: "Slow builds"
**Solution:** Use layer caching, don't use `--no-cache` unless necessary

### Issue: "Large image size"
**Solution:**
- Use `-slim` base image ✅
- Clean up apt cache ✅
- Add proper .dockerignore ✅
- Consider multi-stage build for production ✅

---

## 📝 Which Dockerfile to Use?

### Use `Dockerfile` (current) for:
- ✅ Local development
- ✅ Testing features
- ✅ Learning Docker

### Use `Dockerfile.prod` for:
- ✅ Production deployment
- ✅ Staging environment
- ✅ Performance testing

---

## 🎯 Quick Reference

| What Changed | Rebuild Needed? |
|--------------|----------------|
| Python code | ❌ No (volume mounted) |
| requirements.txt | ✅ Yes |
| Dockerfile | ✅ Yes |
| docker-compose.yml | ❌ No (just restart) |
| .env variables | ❌ No (just restart) |

---

**Your Dockerfile is now production-ready for development!** 🎉

Want to deploy to production? Use `Dockerfile.prod` with these changes in docker-compose:
```yaml
build:
  context: .
  dockerfile: Dockerfile.prod
```
