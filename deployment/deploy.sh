#!/bin/bash
# Deployment script for Earring Generator on Raspberry Pi with SWAG

set -e

echo "=========================================="
echo "Earring Generator - Raspberry Pi Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Project root: $PROJECT_ROOT${NC}"
echo ""

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Python3 is required but not installed.${NC}" >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}npm is required but not installed.${NC}" >&2; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo -e "${RED}pip3 is required but not installed.${NC}" >&2; exit 1; }
echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Step 2: Install backend dependencies
echo "Step 2: Installing backend dependencies..."
cd "$PROJECT_ROOT/backend"
pip3 install -r requirements.txt --user
echo -e "${GREEN}✓ Backend dependencies installed${NC}"
echo ""

# Step 3: Build frontend
echo "Step 3: Building frontend for production..."
cd "$PROJECT_ROOT/frontend"
npm install
npm run build
echo -e "${GREEN}✓ Frontend built successfully${NC}"
echo ""

# Step 4: Install systemd service
echo "Step 4: Installing backend service..."
echo -e "${YELLOW}This step requires sudo access${NC}"
sudo cp "$SCRIPT_DIR/earring-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable earring-backend
echo -e "${GREEN}✓ Service installed${NC}"
echo ""

# Step 5: Start backend
echo "Step 5: Starting backend service..."
sudo systemctl restart earring-backend
sleep 2
if sudo systemctl is-active --quiet earring-backend; then
    echo -e "${GREEN}✓ Backend service is running${NC}"
else
    echo -e "${RED}✗ Backend service failed to start${NC}"
    echo "Check logs with: sudo journalctl -u earring-backend -n 50"
    exit 1
fi
echo ""

# Step 6: SWAG configuration instructions
echo "Step 6: SWAG Configuration"
echo -e "${YELLOW}Manual step required:${NC}"
echo ""
echo "Choose one of the following options:"
echo ""
echo "Option A - Subdomain (e.g., earring.yourdomain.com):"
echo "  sudo cp $SCRIPT_DIR/earring.subdomain.conf /path/to/swag/nginx/proxy-confs/"
echo ""
echo "Option B - Subfolder (e.g., yourdomain.com/earring):"
echo "  sudo cp $SCRIPT_DIR/earring.subfolder.conf /path/to/swag/nginx/proxy-confs/"
echo "  (Note: Subfolder requires frontend base path configuration)"
echo ""
echo "After copying, restart SWAG:"
echo "  docker restart swag"
echo ""

# Step 7: Test backend
echo "Step 7: Testing backend..."
if curl -s http://127.0.0.1:5000/health | grep -q "ok"; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    exit 1
fi
echo ""

echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy nginx config to SWAG (see Step 6 above)"
echo "2. Restart SWAG: docker restart swag"
echo "3. Access your app at your configured domain/subdomain"
echo ""
echo "Useful commands:"
echo "  View backend logs: sudo journalctl -u earring-backend -f"
echo "  Restart backend:   sudo systemctl restart earring-backend"
echo "  Stop backend:      sudo systemctl stop earring-backend"
echo ""
