# 🌐 Nginx Setup for JackStatz Basketball Tracker

## 🚀 Quick Setup (Automated)

Run the automated setup script:

```bash
chmod +x setup-nginx.sh
./setup-nginx.sh
```

This will:
- Install Nginx
- Create the configuration
- Enable the site
- Start Nginx

## 📋 Manual Setup

### 1. Install Nginx
```bash
sudo apt update
sudo apt install nginx -y
```

### 2. Create Site Configuration
```bash
sudo nano /etc/nginx/sites-available/jackstatz
```

Copy the contents from `nginx.conf` and replace:
- `your-domain.com` with your actual domain
- `/path/to/your/jackstatz/` with your project path

### 3. Enable Site
```bash
# Enable your site
sudo ln -s /etc/nginx/sites-available/jackstatz /etc/nginx/sites-enabled/

# Disable default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔒 SSL Setup (HTTPS)

### Option 1: Let's Encrypt (Free SSL)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (optional)
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Option 2: Use SSL Configuration
```bash
# Copy SSL config instead
sudo cp nginx-ssl.conf /etc/nginx/sites-available/jackstatz-ssl
sudo ln -s /etc/nginx/sites-available/jackstatz-ssl /etc/nginx/sites-enabled/
```

## ⚙️ Key Configuration Features

### 🔴 Server-Sent Events (SSE) Support
```nginx
location /events {
    proxy_buffering off;          # Critical for SSE
    proxy_cache off;              # No caching for live data
    proxy_read_timeout 24h;       # Long timeout for persistent connections
    chunked_transfer_encoding off; # Required for SSE
}
```

### 📁 Static File Serving
```nginx
location /static/ {
    alias /path/to/jackstatz/static/;
    expires 1y;                   # Cache static files
    gzip_static on;              # Serve pre-compressed files
}
```

### 🛡️ Security Headers
- X-Frame-Options: Prevent clickjacking
- X-XSS-Protection: XSS protection
- Content-Security-Policy: Restrict resource loading
- HSTS: Force HTTPS (SSL config only)

## 🔧 Troubleshooting

### Check Nginx Status
```bash
sudo systemctl status nginx
sudo nginx -t                    # Test configuration
sudo tail -f /var/log/nginx/error.log
```

### Common Issues

**1. SSE Not Working**
- Check `/events` endpoint configuration
- Ensure `proxy_buffering off`
- Verify Flask app is running on 127.0.0.1:8000

**2. Static Files Not Loading**
- Check static file path in nginx config
- Verify file permissions: `sudo chown -R www-data:www-data /path/to/static/`

**3. 502 Bad Gateway**
- Flask app not running: `gunicorn -k gevent -w 1 -b 127.0.0.1:8000 app:app`
- Check if port 8000 is in use: `sudo lsof -i :8000`

**4. Domain Not Resolving**
- Update DNS A record to point to your server IP
- Wait for DNS propagation (up to 24 hours)

## 🏃‍♂️ Start Your Application

### Development
```bash
cd /path/to/jackstatz
source venv/bin/activate
python app.py
```

### Production
```bash
cd /path/to/jackstatz
source venv/bin/activate
gunicorn -k gevent -w 1 -b 127.0.0.1:8000 app:app
```

### Production with Process Manager
```bash
# Install supervisor
sudo apt install supervisor -y

# Create supervisor config
sudo nano /etc/supervisor/conf.d/jackstatz.conf
```

Supervisor config:
```ini
[program:jackstatz]
command=/path/to/jackstatz/venv/bin/gunicorn -k gevent -w 1 -b 127.0.0.1:8000 app:app
directory=/path/to/jackstatz
user=your-username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/jackstatz.log
```

```bash
# Start with supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start jackstatz
```

## 🎯 Performance Tips

1. **Enable Gzip**: Already configured for CSS/JS compression
2. **Static File Caching**: 1-year cache for static assets
3. **Connection Keep-Alive**: Configured for SSE persistence
4. **Buffer Optimization**: Tuned for real-time updates

## 🔍 Monitoring

### Check Live Connections
```bash
# See active SSE connections
sudo netstat -an | grep :8000 | grep ESTABLISHED

# Monitor Nginx access logs
sudo tail -f /var/log/nginx/access.log
```

Your basketball tracker will be available at `http://your-domain.com` with full SSE support for live updates! 🏀
