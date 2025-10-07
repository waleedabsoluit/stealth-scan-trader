#!/bin/bash
# STEALTH Bot Deployment Script

set -e

echo "🚀 STEALTH Bot Deployment Starting..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build images
echo "🏗️  Building Docker images..."
docker-compose build --no-cache

# Start services
echo "▶️  Starting services..."
docker-compose up -d

# Wait for backend to be healthy
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done

# Initialize database
echo "🗄️  Initializing database..."
docker-compose exec -T backend python -c "
from backend.database import init_db
init_db()
print('Database initialized successfully')
"

echo "✅ Deployment complete!"
echo ""
echo "📊 STEALTH Bot is now running:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
