# 🔴 Nginx Configuration for Server-Sent Events (SSE)

## 🚨 Critical SSE Settings

Your SSE is working locally, but Nginx needs special configuration to support streaming. Here are the **essential settings**:

### 1. **Disable Buffering** (Most Important)
```nginx
location /events {
    proxy_buffering off;           # 🚨 CRITICAL: Disable proxy buffering
    proxy_cache off;               # 🚨 CRITICAL: Disable caching
    add_header X-Accel-Buffering no;  # 🚨 CRITICAL: Disable Nginx buffering
}
```

### 2. **Long Timeouts**
```nginx
proxy_read_timeout 24h;    # Keep SSE connections alive
proxy_send_timeout 24h;    # Allow long-running streams
```

### 3. **HTTP/1.1 Persistent Connections**
```nginx
proxy_http_version 1.1;
proxy_set_header Connection "";
chunked_transfer_encoding off;
```

## 🛠️ Quick Setup

### Option 1: Use the Optimized Config
```bash
# Copy the optimized config
sudo cp nginx-sse-optimized.conf /etc/nginx/sites-available/jackstatz

# Edit with your domain and paths
sudo nano /etc/nginx/sites-available/jackstatz

# Enable the site
sudo ln -sf /etc/nginx/sites-available/jackstatz /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Add SSE Block to Existing Config
If you already have an Nginx config, just add this block:

```nginx
# Add this BEFORE your main location / block
location /events {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # SSE-specific settings
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 24h;
    proxy_connect_timeout 5s;
    proxy_send_timeout 24h;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    chunked_transfer_encoding off;
    add_header X-Accel-Buffering no;
    add_header Cache-Control "no-cache";
}
```

## 🧪 Test SSE Through Nginx

After configuring Nginx, test that SSE works through the proxy:

```bash
# Test direct connection (should work)
curl -N http://localhost:8000/events

# Test through Nginx (should also work after config)
curl -N http://your-domain.com/events
```

## 🔍 Common Issues & Solutions

### Issue 1: "Connection Closed" Immediately
**Problem**: Nginx is buffering the response
**Solution**: Ensure `proxy_buffering off` and `add_header X-Accel-Buffering no`

### Issue 2: SSE Works Locally But Not Through Nginx
**Problem**: Missing SSE-specific headers
**Solution**: Add all the headers from the config above

### Issue 3: Connection Drops After 60 Seconds
**Problem**: Default proxy timeout is too short
**Solution**: Set `proxy_read_timeout 24h`

### Issue 4: CORS Errors in Browser
**Problem**: Missing CORS headers for SSE
**Solution**: Add the CORS headers from the config

## 🎯 Verification Checklist

After setting up Nginx, verify these work:

- [ ] **SSE Connection**: `curl -N http://your-domain.com/events` shows "connected" message
- [ ] **Live Updates**: Changes in one browser appear in another
- [ ] **Long Connections**: SSE stays connected for minutes without dropping
- [ ] **No Buffering**: Updates appear immediately, not in batches

## 🚀 Production Optimization

### For High Traffic:
```nginx
# Increase worker connections
events {
    worker_connections 2048;  # Default is 1024
}

# Optimize for many SSE connections
http {
    keepalive_timeout 65;
    keepalive_requests 1000;
}
```

### SSL/HTTPS Version:
```nginx
# For HTTPS, add these to your SSL server block
location /events {
    # ... all the SSE settings above ...
    
    # Additional SSL-specific headers
    proxy_set_header X-Forwarded-Proto https;
    add_header Strict-Transport-Security "max-age=31536000" always;
}
```

## 🔧 Debugging Commands

```bash
# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check if SSE endpoint is accessible
curl -I http://your-domain.com/events

# Monitor active connections
sudo netstat -an | grep :80 | grep ESTABLISHED

# Test SSE with verbose output
curl -v -N http://your-domain.com/events
```

## 📊 Expected Behavior

With proper Nginx configuration, you should see:

1. **Immediate Connection**: Browser connects to `/events` instantly
2. **Real-time Updates**: Changes appear in other browsers within 1-2 seconds
3. **Persistent Connection**: SSE stays connected for hours
4. **No Buffering**: Updates stream immediately, not in batches

Your basketball tracker's live updates will work perfectly across multiple browsers! 🏀
