#!/bin/bash
set -e

echo "🚀 Starting NuiFlo WorkForce API deployment..."

# Run database migrations
echo "📊 Running database migrations..."
cd workforce_api
python -m alembic upgrade head
cd ..

echo "✅ Migrations completed successfully"

# Start the FastAPI server
echo "🌐 Starting API server..."
uvicorn main:app --host 0.0.0.0 --port $PORT

echo "🎉 Deployment completed!" 