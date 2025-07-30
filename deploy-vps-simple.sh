#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VPS_IP="37.27.223.110"
VPS_USER="root"
CONTAINER_NAME="nuiflo-workforce-api"
IMAGE_NAME="nuiflo-workforce-api:latest"

echo -e "${GREEN}🚀 NuiFlo WorkForce API Deployment (Auth Fixed)${NC}"
echo "=================================="

# Check if files exist
if [ ! -f "nuiflo-api-auth-fixed.tar.gz" ]; then
    echo -e "${RED}❌ nuiflo-api-auth-fixed.tar.gz not found!${NC}"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml not found!${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "VPS IP: $VPS_IP"
echo "VPS User: $VPS_USER"
echo "Container: $CONTAINER_NAME"
echo "Image: $IMAGE_NAME"
echo

echo -e "${YELLOW}📤 Copying files to VPS...${NC}"
scp nuiflo-api-auth-fixed.tar.gz docker-compose.yml .env $VPS_USER@$VPS_IP:~/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Files copied successfully${NC}"
else
    echo -e "${RED}❌ Failed to copy files${NC}"
    exit 1
fi

echo -e "${YELLOW}🔧 Deploying on VPS...${NC}"
ssh $VPS_USER@$VPS_IP << 'EOF'
    echo "Stopping existing container..."
    docker-compose down
    
    echo "Removing old image..."
    docker rmi nuiflo-workforce-api:latest 2>/dev/null || true
    
    echo "Loading new image..."
    gunzip -c nuiflo-api-auth-fixed.tar.gz | docker load
    
    echo "Starting container..."
    docker-compose up -d
    
    echo "Checking status..."
    docker ps
    
    echo "Container logs:"
    docker logs nuiflo-workforce-api --tail 20
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo -e "${YELLOW}🌐 API should be available at: https://api.nuiflo.com${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi 