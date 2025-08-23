#!/bin/bash
# Setup script for Nginx with JackStatz Basketball Tracker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏀 Setting up Nginx for JackStatz Basketball Tracker${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}"
   exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., stats.example.com): " DOMAIN
if [[ -z "$DOMAIN" ]]; then
    echo -e "${RED}Domain name is required${NC}"
    exit 1
fi

# Get project path
read -p "Enter full path to your jackstatz project (e.g., /home/user/jackstatz): " PROJECT_PATH
if [[ ! -d "$PROJECT_PATH" ]]; then
    echo -e "${RED}Project path does not exist: $PROJECT_PATH${NC}"
    exit 1
fi

echo -e "${YELLOW}Installing Nginx...${NC}"
sudo apt update
sudo apt install nginx -y

echo -e "${YELLOW}Creating Nginx configuration...${NC}"

# Create nginx config
sudo tee /etc/nginx/sites-available/jackstatz > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # Static files
    location /static/ {
        alias $PROJECT_PATH/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Server-Sent Events endpoint (critical for live updates)
    location /events {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # SSE specific settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 24h;
        proxy_connect_timeout 5s;
        proxy_send_timeout 24h;
        
        # Keep connection alive
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Block sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(env|git)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# Redirect www to non-www
server {
    listen 80;
    server_name www.$DOMAIN;
    return 301 http://$DOMAIN\$request_uri;
}
EOF

echo -e "${YELLOW}Enabling site...${NC}"
sudo ln -sf /etc/nginx/sites-available/jackstatz /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo -e "${YELLOW}Testing Nginx configuration...${NC}"
sudo nginx -t

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
    
    echo -e "${YELLOW}Starting Nginx...${NC}"
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    echo -e "${GREEN}✅ Nginx setup complete!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Make sure your Flask app is running on port 8000:"
    echo "   cd $PROJECT_PATH"
    echo "   source venv/bin/activate"
    echo "   gunicorn -k gevent -w 1 -b 127.0.0.1:8000 app:app"
    echo ""
    echo "2. Point your domain DNS to this server's IP address"
    echo ""
    echo "3. Optional - Set up SSL with Let's Encrypt:"
    echo "   sudo apt install certbot python3-certbot-nginx"
    echo "   sudo certbot --nginx -d $DOMAIN"
    echo ""
    echo -e "${GREEN}🏀 Your basketball tracker will be available at: http://$DOMAIN${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    exit 1
fi
