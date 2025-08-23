# 🚀 Deployment Guide

## 📦 Requirements Files

Choose the appropriate requirements file based on your deployment scenario:

### 1. **Minimal Install** (Fastest - ~30 seconds)
```bash
pip install -r requirements-minimal.txt
```
- Only core dependencies (Flask, Supabase, python-dotenv)
- Best for: Quick testing, development

### 2. **Full Install** (Complete - ~60 seconds)
```bash
pip install -r requirements.txt
```
- All dependencies with exact versions
- Best for: Full functionality, staging

### 3. **Production Install** (Optimized - ~90 seconds)
```bash
pip install -r requirements-production.txt
```
- Includes Gunicorn + Gevent for production
- Best for: Production deployments

## 🖥️ Server Installation Commands

### Ubuntu/Debian VPS Setup
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and Git
sudo apt install python3 python3-pip python3-venv git -y

# 3. Clone repository
git clone https://github.com/yourusername/jackstatz.git
cd jackstatz

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies (choose one)
pip install -r requirements-minimal.txt     # Fastest
# OR
pip install -r requirements.txt             # Complete
# OR  
pip install -r requirements-production.txt  # Production

# 6. Set up environment variables
nano .env
# Add your Supabase credentials:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key

# 7. Run the application
python app.py                    # Development
# OR
gunicorn -k gevent -w 1 -b 0.0.0.0:8000 app:app  # Production
```

## ⚡ Speed Optimizations

### Pre-download Wheels (Fastest Install)
```bash
# Create a wheel cache for even faster installs
pip wheel -r requirements.txt -w ./wheels
pip install --find-links ./wheels -r requirements.txt
```

### Use pip-tools for Dependency Management
```bash
# Install pip-tools
pip install pip-tools

# Generate locked requirements
pip-compile requirements.in

# Install from locked file
pip-sync requirements.txt
```

## 🔧 Production Configuration

### Gunicorn Configuration (`gunicorn.conf.py`)
```python
bind = "0.0.0.0:8000"
workers = 1
worker_class = "gevent"
worker_connections = 1000
keepalive = 30
max_requests = 1000
max_requests_jitter = 100
timeout = 30
```

### Nginx Configuration (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # SSE specific headers
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

## 📊 Installation Time Estimates

| Requirements File | Install Time | Packages | Use Case |
|------------------|--------------|----------|----------|
| `requirements-minimal.txt` | ~30 seconds | 15 | Quick testing |
| `requirements.txt` | ~60 seconds | 38 | Full features |
| `requirements-production.txt` | ~90 seconds | 40 | Production |

## 🐳 Docker Option (Alternative)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-production.txt .
RUN pip install --no-cache-dir -r requirements-production.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "-k", "gevent", "-w", "1", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t jackstatz .
docker run -p 8000:8000 --env-file .env jackstatz
```

## 🔍 Troubleshooting

### Common Issues:
1. **Slow install**: Use `requirements-minimal.txt` first
2. **Version conflicts**: Use exact versions from `requirements.txt`
3. **SSE not working**: Ensure Gunicorn uses gevent worker
4. **Port conflicts**: Change port in app.py or use environment variable

### Performance Tips:
- Use `--no-cache-dir` with pip to save space
- Use `--upgrade-strategy only-if-needed` for updates
- Consider using `uv` instead of pip for faster installs
