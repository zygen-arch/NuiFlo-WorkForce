#!/bin/bash
set -e

echo "🚀 Deploying NuiFlo WorkForce API to VPS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VPS_IP="37.27.223.110"
VPS_USER="root"  # Change this to your VPS username (e.g., "ubuntu", "partha", etc.)
CONTAINER_NAME="nuiflo-workforce-api"
IMAGE_NAME="nuiflo-workforce-api:latest"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "VPS IP: $VPS_IP"
echo "VPS User: $VPS_USER"
echo "Container: $CONTAINER_NAME"
echo "Image: $IMAGE_NAME"
echo

# Note: SSH connection will prompt for password when needed
echo -e "${YELLOW}🔐 SSH Configuration:${NC}"
echo "Using password authentication - you'll be prompted for password"
echo "Make sure you can connect manually: ssh $VPS_USER@$VPS_IP"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create a .env file with your environment variables:"
    echo "DATABASE_URL=..."
    echo "SUPABASE_URL=..."
    echo "SUPABASE_KEY=..."
    echo "OPENAI_API_KEY=..."
    echo "ANTHROPIC_API_KEY=..."
    exit 1
fi

echo -e "${GREEN}✅ Environment file found${NC}"

# Build the Docker image from the new backend directory
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -f backend/Dockerfile -t $IMAGE_NAME ./backend

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Save the image as tar file
echo -e "${YELLOW}📦 Saving Docker image...${NC}"
docker save $IMAGE_NAME | gzip > nuiflo-api.tar.gz

# Copy files to VPS
echo -e "${YELLOW}📤 Copying files to VPS...${NC}"
scp nuiflo-api.tar.gz docker-compose.yml .env $VPS_USER@$VPS_IP:/root/

# Deploy on VPS
echo -e "${YELLOW}🚀 Deploying on VPS...${NC}"
ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e
    
    echo "📥 Loading Docker image..."
    docker load < nuiflo-api.tar.gz
    
    echo "🛑 Stopping and removing existing containers..."
    docker-compose down || true
    docker rm -f nuiflo-workforce-api || true
    
    echo "🧹 Cleaning up old images..."
    docker image prune -f
    
    echo "🚀 Starting new container..."
    docker-compose up -d
    
    echo "⏳ Waiting for container to start..."
    sleep 10
    
    echo "🔍 Checking container status..."
    docker-compose ps
    
    echo "🏥 Checking health..."
    docker-compose logs --tail=20
EOF

# Clean up local files
echo -e "${YELLOW}🧹 Cleaning up local files...${NC}"
rm -f nuiflo-api.tar.gz

echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo -e "${YELLOW}📊 API should be available at: http://$VPS_IP:8000${NC}"
echo -e "${YELLOW}📚 API docs: http://$VPS_IP:8000/docs${NC}"
echo -e "${YELLOW}🔍 Health check: http://$VPS_IP:8000/health/ping${NC}" 