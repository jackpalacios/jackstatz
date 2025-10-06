#!/bin/bash
# Complete Cloudflare Tunnel setup for JackStatz Basketball Tracker

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏀 Setting up Cloudflare Tunnel for JackStatz${NC}"
echo "=============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Don't run this script as root${NC}"
   exit 1
fi

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo -e "${RED}❌ cloudflared not found. Run install_cloudflared.sh first${NC}"
    exit 1
fi

# Get configuration
echo -e "${YELLOW}Configuration Setup${NC}"
read -p "Enter your domain name (e.g., stats.example.com): " DOMAIN
if [[ -z "$DOMAIN" ]]; then
    echo -e "${RED}Domain name is required${NC}"
    exit 1
fi

read -p "Enter your project path (default: $(pwd)): " PROJECT_PATH
PROJECT_PATH=${PROJECT_PATH:-$(pwd)}

if [[ ! -f "$PROJECT_PATH/app.py" ]]; then
    echo -e "${RED}❌ app.py not found in $PROJECT_PATH${NC}"
    exit 1
fi

echo -e "${YELLOW}1. Authenticating with Cloudflare...${NC}"
echo "This will open a browser window for authentication"
cloudflared tunnel login

echo -e "${YELLOW}2. Creating tunnel...${NC}"
if cloudflared tunnel list | grep -q "jackstatz-tunnel"; then
    echo -e "${GREEN}✅ Tunnel 'jackstatz-tunnel' already exists${NC}"
else
    cloudflared tunnel create jackstatz-tunnel
    echo -e "${GREEN}✅ Created tunnel 'jackstatz-tunnel'${NC}"
fi

echo -e "${YELLOW}3. Setting up DNS routing...${NC}"
cloudflared tunnel route dns jackstatz-tunnel "$DOMAIN"
echo -e "${GREEN}✅ DNS route created for $DOMAIN${NC}"

echo -e "${YELLOW}4. Configuring tunnel...${NC}"

# Update cloudflared.yml with actual domain and paths
sed -i.bak "s|your-domain.com|$DOMAIN|g" "$PROJECT_PATH/cloudflared.yml"
sed -i.bak "s|/home/user|$HOME|g" "$PROJECT_PATH/cloudflared.yml"

# Copy configuration to system location
sudo cp "$PROJECT_PATH/cloudflared.yml" /etc/cloudflared/
sudo chown root:root /etc/cloudflared/cloudflared.yml
sudo chmod 644 /etc/cloudflared/cloudflared.yml

echo -e "${GREEN}✅ Tunnel configuration installed${NC}"

echo -e "${YELLOW}5. Installing Gunicorn...${NC}"
source "$PROJECT_PATH/venv/bin/activate"
pip install gunicorn gevent

echo -e "${YELLOW}6. Setting up systemd services...${NC}"

# Update service files with actual paths and user
USER=$(whoami)
sed -i.bak "s|your-username|$USER|g" "$PROJECT_PATH/jackstatz.service"
sed -i.bak "s|/path/to/jackstatz|$PROJECT_PATH|g" "$PROJECT_PATH/jackstatz.service"

sed -i.bak "s|your-username|$USER|g" "$PROJECT_PATH/cloudflared.service"
sed -i.bak "s|/path/to/jackstatz|$PROJECT_PATH|g" "$PROJECT_PATH/cloudflared.service"

# Install systemd services
sudo cp "$PROJECT_PATH/jackstatz.service" /etc/systemd/system/
sudo cp "$PROJECT_PATH/cloudflared.service" /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

echo -e "${GREEN}✅ Systemd services installed${NC}"

echo -e "${YELLOW}7. Starting services...${NC}"

# Enable and start Flask app
sudo systemctl enable jackstatz
sudo systemctl start jackstatz

# Wait a moment for Flask to start
sleep 3

# Check if Flask is running
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo -e "${GREEN}✅ Flask app is running${NC}"
else
    echo -e "${RED}❌ Flask app failed to start${NC}"
    echo "Check logs: sudo journalctl -u jackstatz -f"
    exit 1
fi

# Enable and start Cloudflare tunnel
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# Wait for tunnel to start
sleep 5

echo -e "${YELLOW}8. Testing deployment...${NC}"

# Test the tunnel
if curl -s "https://$DOMAIN/" > /dev/null; then
    echo -e "${GREEN}✅ Website accessible through Cloudflare!${NC}"
else
    echo -e "${YELLOW}⚠️ Website not yet accessible (DNS may still be propagating)${NC}"
fi

# Test SSE endpoint
echo -e "${YELLOW}Testing SSE endpoint...${NC}"
if timeout 5 curl -s -N "https://$DOMAIN/events" | head -1 | grep -q "data:"; then
    echo -e "${GREEN}✅ SSE working through Cloudflare!${NC}"
else
    echo -e "${YELLOW}⚠️ SSE endpoint may need a moment to initialize${NC}"
fi

echo ""
echo -e "${BLUE}=============================================="
echo -e "🎉 Cloudflare Tunnel Setup Complete!"
echo -e "${NC}"
echo -e "${GREEN}Your basketball tracker is now available at:${NC}"
echo -e "${BLUE}https://$DOMAIN${NC}"
echo ""
echo -e "${YELLOW}Service Management:${NC}"
echo "• Flask app: sudo systemctl {start|stop|restart|status} jackstatz"
echo "• Cloudflare tunnel: sudo systemctl {start|stop|restart|status} cloudflared"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "• Flask app: sudo journalctl -u jackstatz -f"
echo "• Cloudflare tunnel: sudo journalctl -u cloudflared -f"
echo ""
echo -e "${YELLOW}Configuration files:${NC}"
echo "• Tunnel config: /etc/cloudflared/cloudflared.yml"
echo "• Flask service: /etc/systemd/system/jackstatz.service"
echo "• Cloudflare service: /etc/systemd/system/cloudflared.service"
echo ""
echo -e "${GREEN}🏀 Your basketball stats tracker is now globally accessible with SSE support!${NC}"
