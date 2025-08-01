#!/bin/bash
set -e

echo "🚀 Deploying Fixed NuiFlo WorkForce API..."

# Configuration
VPS_IP="37.27.223.110"
VPS_USER="root"

echo "📦 Creating fixed image tar..."
docker save nuiflo-workforce-api:latest | gzip > nuiflo-api-fixed.tar.gz

echo "📤 Copying files to VPS..."
scp nuiflo-api-fixed.tar.gz docker-compose.yml .env $VPS_USER@$VPS_IP:/root/

echo "🚀 Deploying on VPS..."
ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e
    
    echo "📥 Loading fixed Docker image..."
    docker load < nuiflo-api-fixed.tar.gz
    
    echo "🛑 Stopping and removing existing containers..."
    docker-compose down || true
    docker rm -f nuiflo-workforce-api || true
    
    echo "🧹 Cleaning up old images..."
    docker image prune -f
    
    echo "🚀 Starting new container..."
    docker-compose up -d
    
    echo "⏳ Waiting for container to start..."
    sleep 15
    
    echo "🔍 Checking container status..."
    docker-compose ps
    
    echo "🏥 Checking health..."
    docker-compose logs --tail=20
EOF

echo "🧹 Cleaning up local files..."
rm -f nuiflo-api-fixed.tar.gz

echo "🎉 Fixed deployment completed!"
echo "📊 API should be available at: http://$VPS_IP:8000"
echo "📚 API docs: http://$VPS_IP:8000/docs"
echo "🔍 Health check: http://$VPS_IP:8000/health/ping" 