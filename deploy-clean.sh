#!/bin/bash
echo "🚀 Deploying clean NuiFlo WorkForce API..."

# Load the image
docker load < nuiflo-api-clean.tar.gz

# Start the container
docker run -d \
  --name nuiflo-workforce-api \
  --network host \
  --env-file .env \
  --restart unless-stopped \
  nuiflo-workforce-api:latest

echo "✅ Deployment complete!"
docker ps | grep nuiflo
