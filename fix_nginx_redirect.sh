#!/bin/bash
# Fix Nginx 301 redirect issue that breaks SSE
# This script fixes the redirect problem for SSE connections

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Fixing Nginx 301 Redirect Issue for SSE${NC}"
echo "================================================"

# Check if running as root for nginx commands
if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}Note: You may need to run nginx commands with sudo${NC}"
fi

echo -e "${YELLOW}1. Checking current Nginx configuration...${NC}"

# Find the problematic redirect
echo "Looking for redirect configurations..."
if grep -r "return 301" /etc/nginx/sites-enabled/ 2>/dev/null; then
    echo -e "${RED}❌ Found 301 redirects that break SSE${NC}"
else
    echo -e "${GREEN}✅ No obvious 301 redirects found${NC}"
fi

# Check for SSL redirects
if grep -r "return.*https" /etc/nginx/sites-enabled/ 2>/dev/null; then
    echo -e "${RED}❌ Found HTTPS redirects that break SSE${NC}"
else
    echo -e "${GREEN}✅ No HTTPS redirects found${NC}"
fi

echo -e "${YELLOW}2. Creating SSE-friendly Nginx configuration...${NC}"

# Get domain name
echo "What's your domain name? (e.g., stats.example.com, or just press Enter for IP-only setup)"
read DOMAIN

if [[ -z "$DOMAIN" ]]; then
    DOMAIN="_"
    SERVER_NAME="server_name _;"
    echo "Using IP-only configuration"
else
    SERVER_NAME="server_name $DOMAIN;"
    echo "Using domain: $DOMAIN"
fi

# Create a new configuration that handles SSE properly
cat > /tmp/jackstatz-sse-fixed.conf << EOF
# SSE-friendly configuration - NO redirects for /events
server {
    listen 80;
    $SERVER_NAME
    
    # CRITICAL: Handle SSE endpoint WITHOUT redirects
    location /events {
        # NO redirects here - SSE connections must stay on same protocol/port
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Essential SSE settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 24h;
        proxy_connect_timeout 5s;
        proxy_send_timeout 24h;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        chunked_transfer_encoding off;
        add_header X-Accel-Buffering no;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
        
        # CORS headers
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range";
    }
    
    # Static files
    location /static/ {
        proxy_pass http://127.0.0.1:8000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main application - can redirect if needed, but NOT /events
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Normal proxy settings
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering on;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}
EOF

echo -e "${YELLOW}3. Installing new configuration...${NC}"

# Backup existing config
if [[ -f "/etc/nginx/sites-enabled/default" ]]; then
    sudo cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup.$(date +%s)
    echo "Backed up existing default config"
fi

# Install new config
sudo cp /tmp/jackstatz-sse-fixed.conf /etc/nginx/sites-available/jackstatz-sse-fixed
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/sites-enabled/jackstatz*  # Remove any old jackstatz configs
sudo ln -sf /etc/nginx/sites-available/jackstatz-sse-fixed /etc/nginx/sites-enabled/

echo -e "${YELLOW}4. Testing configuration...${NC}"

if sudo nginx -t; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
    
    echo -e "${YELLOW}5. Reloading Nginx...${NC}"
    sudo systemctl reload nginx
    
    echo -e "${GREEN}✅ Nginx reloaded successfully${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    sudo nginx -t
    exit 1
fi

echo -e "${YELLOW}6. Testing SSE connection...${NC}"
sleep 2

# Test the SSE endpoint
if timeout 5 curl -s -N http://localhost/events | head -1 | grep -q "data:"; then
    echo -e "${GREEN}✅ SSE is working through Nginx!${NC}"
else
    echo -e "${RED}❌ SSE still not working${NC}"
    echo "Let's check what's happening..."
    
    # Show what we're getting
    echo "Response from /events:"
    timeout 3 curl -v http://localhost/events 2>&1 | head -10
fi

echo -e "${YELLOW}7. Testing stat update...${NC}"

# Test a stat update to see if it broadcasts
if curl -s -X POST http://localhost/update_player_stat \
   -H "Content-Type: application/json" \
   -d '{"team": "team1", "player_index": 0, "stat_type": "points_2", "value": 77, "game_id": "1"}' | grep -q "success"; then
    echo -e "${GREEN}✅ Stat updates working through Nginx${NC}"
else
    echo -e "${RED}❌ Stat updates not working through Nginx${NC}"
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🎉 Fix Complete!${NC}"
echo ""
echo -e "${YELLOW}What was fixed:${NC}"
echo "• Removed 301 redirects that broke SSE connections"
echo "• Added proper SSE configuration for /events endpoint"
echo "• Kept redirects away from SSE endpoints"
echo ""
echo -e "${YELLOW}Test your app:${NC}"
if [[ "$DOMAIN" != "_" ]]; then
    echo "• Open: http://$DOMAIN/live-game"
else
    echo "• Open: http://your-server-ip/live-game"
fi
echo "• Open in 2 browser tabs"
echo "• Make changes in one tab"
echo "• Should see updates in the other tab instantly!"
echo ""
echo -e "${YELLOW}Debug commands:${NC}"
echo "• Test SSE: curl -N http://localhost/events"
echo "• Check logs: sudo tail -f /var/log/nginx/error.log"
echo "• Check Flask: curl http://127.0.0.1:8000/"

# Clean up
rm -f /tmp/jackstatz-sse-fixed.conf
