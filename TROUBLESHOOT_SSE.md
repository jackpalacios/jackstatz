# 🚨 SSE Not Working on Server - Troubleshooting Guide

Since your SSE works locally but not on the server, here's a systematic approach to fix it:

## 🔧 Quick Fix (Run This First)

```bash
# On your server, run the automated fix script:
chmod +x fix_sse_server.sh
./fix_sse_server.sh
```

This script will:
- ✅ Check if Flask is running
- ✅ Test direct SSE connection
- ✅ Fix Nginx configuration
- ✅ Test SSE through Nginx
- ✅ Verify stat updates work

## 🔍 Manual Debugging Steps

### 1. **Check Flask App is Running**
```bash
# Test if Flask is accessible
curl http://127.0.0.1:8000/

# If not running, start it:
cd /path/to/jackstatz
source venv/bin/activate
python app.py &
```

### 2. **Test Direct SSE (Bypass Nginx)**
```bash
# This should show "connected" message and heartbeats
curl -N http://127.0.0.1:8000/events
```

If this doesn't work, the problem is in your Flask app, not Nginx.

### 3. **Check Nginx Configuration**
```bash
# Test nginx config
sudo nginx -t

# Check if your site is enabled
ls -la /etc/nginx/sites-enabled/

# Look for SSE configuration
grep -r "proxy_buffering off" /etc/nginx/sites-enabled/
```

### 4. **Test SSE Through Nginx**
```bash
# This should also show SSE messages
curl -N http://localhost/events
# OR
curl -N http://your-domain.com/events
```

## 🚨 Common Issues & Fixes

### Issue 1: Flask App Not Running
**Symptoms**: `curl http://127.0.0.1:8000/` fails
**Fix**:
```bash
cd /path/to/jackstatz
source venv/bin/activate
nohup python app.py > flask.log 2>&1 &
```

### Issue 2: Direct SSE Fails
**Symptoms**: `curl -N http://127.0.0.1:8000/events` hangs or errors
**Fix**: Check Flask logs for errors:
```bash
tail -f flask.log
```

### Issue 3: Nginx Doesn't Have SSE Config
**Symptoms**: SSE works direct but not through Nginx
**Fix**: Add this to your Nginx config:
```nginx
location /events {
    proxy_pass http://127.0.0.1:8000;
    proxy_buffering off;              # CRITICAL
    proxy_cache off;                  # CRITICAL
    add_header X-Accel-Buffering no;  # CRITICAL
    proxy_read_timeout 24h;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    chunked_transfer_encoding off;
}
```

### Issue 4: Wrong Nginx Site Enabled
**Symptoms**: Nginx serves default page instead of your app
**Fix**:
```bash
sudo rm /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/your-site /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### Issue 5: Firewall Blocking Connections
**Symptoms**: Can't access from external browsers
**Fix**:
```bash
sudo ufw allow 80
sudo ufw allow 8000  # For testing
```

### Issue 6: Production Server (Gunicorn) Issues
**Symptoms**: SSE works with `python app.py` but not with Gunicorn
**Fix**: Use gevent worker:
```bash
gunicorn -k gevent -w 1 -b 127.0.0.1:8000 app:app
```

## 🧪 Browser Testing

### Open Browser Developer Tools:
1. **Console Tab**: Look for SSE connection messages
2. **Network Tab**: Check if `/events` request is persistent
3. **Look for errors**: CORS, connection refused, etc.

### Expected Browser Console Output:
```
📡 Received SSE update: {type: "connected", message: "SSE connection established"}
✅ SSE connection established
🟢 Live Connected
```

## 🔍 Advanced Debugging

### Check Server Logs:
```bash
# Flask app logs
tail -f flask.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -f -u nginx
```

### Check Network Connections:
```bash
# See active connections to port 8000
sudo netstat -tulpn | grep :8000

# See active connections to port 80
sudo netstat -tulpn | grep :80

# Check if SSE connections are persistent
sudo netstat -an | grep ESTABLISHED | grep :80
```

### Test with Different Tools:
```bash
# Test with curl (verbose)
curl -v -N http://your-domain.com/events

# Test with wget
wget -O - http://your-domain.com/events

# Test from another server
curl -N http://your-server-ip/events
```

## 🎯 Final Verification

After fixing, you should see:

1. **Direct SSE works**: `curl -N http://127.0.0.1:8000/events`
2. **Nginx SSE works**: `curl -N http://localhost/events`  
3. **Browser shows**: 🟢 Live Connected
4. **Multi-browser updates**: Changes in one browser appear in another instantly

## 📞 Still Not Working?

If none of the above fixes work, run the debug script and share the output:

```bash
python3 debug_sse_server.py > sse_debug.log 2>&1
cat sse_debug.log
```

The most common issue is **Nginx buffering** - make sure you have `proxy_buffering off` in your `/events` location block!
