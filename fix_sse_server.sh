#!/bin/bash
# SSE Server Fix Script
# Run this on your Ubuntu server to fix SSE issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏀 SSE Server Fix Script${NC}"
echo "=================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Don't run this as root (except for nginx commands)${NC}"
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check Flask app
echo -e "${YELLOW}1. Checking Flask app...${NC}"
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo -e "${GREEN}✅ Flask app is running${NC}"
else
    echo -e "${RED}❌ Flask app not running${NC}"
    echo "Starting Flask app..."
    
    # Find the project directory
    if [[ -f "app.py" ]]; then
        PROJECT_DIR=$(pwd)
    else
        echo "Enter your project path (e.g., /home/user/jackstatz):"
        read PROJECT_DIR
    fi
    
    cd "$PROJECT_DIR"
    
    # Activate virtual environment and start app
    if [[ -d "venv" ]]; then
        source venv/bin/activate
        echo "Starting Flask app in background..."
        nohup python app.py > flask.log 2>&1 &
        sleep 3
        
        if curl -s http://127.0.0.1:8000/ > /dev/null; then
            echo -e "${GREEN}✅ Flask app started successfully${NC}"
        else
            echo -e "${RED}❌ Failed to start Flask app${NC}"
            echo "Check flask.log for errors"
            exit 1
        fi
    else
        echo -e "${RED}❌ Virtual environment not found${NC}"
        exit 1
    fi
fi

# 2. Test direct SSE
echo -e "${YELLOW}2. Testing direct SSE connection...${NC}"
if timeout 5 curl -N http://127.0.0.1:8000/events 2>/dev/null | head -1 | grep -q "data:"; then
    echo -e "${GREEN}✅ Direct SSE working${NC}"
else
    echo -e "${RED}❌ Direct SSE not working${NC}"
    echo "Check your Flask app SSE implementation"
fi

# 3. Check Nginx
echo -e "${YELLOW}3. Checking Nginx...${NC}"
if command_exists nginx; then
    if sudo nginx -t 2>/dev/null; then
        echo -e "${GREEN}✅ Nginx config is valid${NC}"
    else
        echo -e "${RED}❌ Nginx config has errors${NC}"
        sudo nginx -t
        exit 1
    fi
    
    # Check if nginx is running
    if pgrep nginx > /dev/null; then
        echo -e "${GREEN}✅ Nginx is running${NC}"
    else
        echo -e "${YELLOW}⚠️ Starting Nginx...${NC}"
        sudo systemctl start nginx
    fi
else
    echo -e "${RED}❌ Nginx not installed${NC}"
    echo "Install nginx first: sudo apt install nginx"
    exit 1
fi

# 4. Check Nginx SSE configuration
echo -e "${YELLOW}4. Checking Nginx SSE configuration...${NC}"

# Look for SSE configuration in enabled sites
SSE_CONFIG_FOUND=false
for site in /etc/nginx/sites-enabled/*; do
    if [[ -f "$site" ]] && grep -q "location /events" "$site"; then
        if grep -q "proxy_buffering off" "$site"; then
            echo -e "${GREEN}✅ Found SSE configuration in $(basename $site)${NC}"
            SSE_CONFIG_FOUND=true
            break
        fi
    fi
done

if [[ "$SSE_CONFIG_FOUND" = false ]]; then
    echo -e "${RED}❌ No proper SSE configuration found${NC}"
    echo -e "${YELLOW}Creating SSE configuration...${NC}"
    
    # Create a minimal SSE config
    sudo tee /etc/nginx/sites-available/jackstatz-sse > /dev/null <<'EOF'
server {
    listen 80 default_server;
    server_name _;
    
    # SSE endpoint - CRITICAL CONFIGURATION
    location /events {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # ESSENTIAL SSE SETTINGS
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
        add_header Access-Control-Allow-Origin "*";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
    
    # Enable the site
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo ln -sf /etc/nginx/sites-available/jackstatz-sse /etc/nginx/sites-enabled/
    
    # Test and reload
    if sudo nginx -t; then
        sudo systemctl reload nginx
        echo -e "${GREEN}✅ SSE configuration applied${NC}"
    else
        echo -e "${RED}❌ Failed to apply SSE configuration${NC}"
        exit 1
    fi
fi

# 5. Test SSE through Nginx
echo -e "${YELLOW}5. Testing SSE through Nginx...${NC}"
sleep 2  # Give nginx time to reload

if timeout 5 curl -N http://localhost/events 2>/dev/null | head -1 | grep -q "data:"; then
    echo -e "${GREEN}✅ SSE working through Nginx!${NC}"
else
    echo -e "${RED}❌ SSE not working through Nginx${NC}"
    echo "Checking nginx error logs..."
    sudo tail -5 /var/log/nginx/error.log
fi

# 6. Test stat update
echo -e "${YELLOW}6. Testing stat update broadcast...${NC}"
if curl -s -X POST http://127.0.0.1:8000/update_player_stat \
   -H "Content-Type: application/json" \
   -d '{"team": "team1", "player_index": 0, "stat_type": "points_2", "value": 42, "game_id": "1"}' | grep -q "success"; then
    echo -e "${GREEN}✅ Stat updates working${NC}"
else
    echo -e "${RED}❌ Stat updates not working${NC}"
fi

echo ""
echo -e "${BLUE}=================================="
echo -e "🎯 FINAL TEST:"
echo -e "${NC}Open two browser tabs to your server:"
echo -e "Tab 1: http://your-server-ip/live-game"
echo -e "Tab 2: http://your-server-ip/live-game"
echo ""
echo -e "In Tab 1: Click a stat button"
echo -e "In Tab 2: Should see the update instantly!"
echo ""
echo -e "${GREEN}If it works: 🎉 SSE is fixed!"
echo -e "${RED}If not: Check browser console for errors${NC}"

# 7. Show debugging info
echo -e "${YELLOW}7. Debugging info:${NC}"
echo "Flask app log: tail -f flask.log"
echo "Nginx error log: sudo tail -f /var/log/nginx/error.log"
echo "Test SSE directly: curl -N http://127.0.0.1:8000/events"
echo "Test SSE via Nginx: curl -N http://localhost/events"
