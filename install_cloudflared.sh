#!/bin/bash
# Install Cloudflare Tunnel (cloudflared) on Ubuntu/Debian

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌐 Installing Cloudflare Tunnel (cloudflared)${NC}"
echo "=================================================="

# Detect architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        ARCH="amd64"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
    armv7l)
        ARCH="arm"
        ;;
    *)
        echo -e "${RED}❌ Unsupported architecture: $ARCH${NC}"
        exit 1
        ;;
esac

echo -e "${YELLOW}Detected architecture: $ARCH${NC}"

# Download and install cloudflared
echo -e "${YELLOW}1. Downloading cloudflared...${NC}"
CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}"

if command -v wget >/dev/null 2>&1; then
    wget -O cloudflared "$CLOUDFLARED_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -L -o cloudflared "$CLOUDFLARED_URL"
else
    echo -e "${RED}❌ Neither wget nor curl found. Please install one of them.${NC}"
    exit 1
fi

echo -e "${YELLOW}2. Installing cloudflared...${NC}"
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Verify installation
if cloudflared version >/dev/null 2>&1; then
    echo -e "${GREEN}✅ cloudflared installed successfully${NC}"
    cloudflared version
else
    echo -e "${RED}❌ cloudflared installation failed${NC}"
    exit 1
fi

echo -e "${YELLOW}3. Setting up cloudflared user and directories...${NC}"

# Create cloudflared user (if it doesn't exist)
if ! id "cloudflared" &>/dev/null; then
    sudo useradd -r -s /bin/false cloudflared
    echo -e "${GREEN}✅ Created cloudflared user${NC}"
else
    echo -e "${GREEN}✅ cloudflared user already exists${NC}"
fi

# Create directories
sudo mkdir -p /etc/cloudflared
sudo mkdir -p /var/log/cloudflared
sudo chown cloudflared:cloudflared /var/log/cloudflared

echo -e "${GREEN}✅ Cloudflared installation complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Authenticate: cloudflared tunnel login"
echo "2. Create tunnel: cloudflared tunnel create jackstatz-tunnel"
echo "3. Configure DNS: cloudflared tunnel route dns jackstatz-tunnel your-domain.com"
echo "4. Copy cloudflared.yml to /etc/cloudflared/"
echo "5. Start tunnel: cloudflared tunnel run jackstatz-tunnel"
echo ""
echo -e "${BLUE}📖 See setup_cloudflare_tunnel.sh for automated setup${NC}"
