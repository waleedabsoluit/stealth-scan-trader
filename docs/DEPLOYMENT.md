# STEALTH Bot Deployment Guide

## Quick Start (Docker)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### One-Command Deployment

```bash
# Clone the repository (or navigate to project directory)
cd stealth-scan-trader-main

# Make deployment script executable (Linux/Mac)
chmod +x deploy.sh

# Deploy
./deploy.sh
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Manual Docker Deployment

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Local Development Setup

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize Database**
```bash
python -c "from backend.database import init_db; init_db()"
```

4. **Run Backend Server**
```bash
# From project root
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install Dependencies**
```bash
npm install
```

2. **Run Development Server**
```bash
npm run dev
```

3. **Build for Production**
```bash
npm run build
```

## Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Edit with your settings
nano .env
```

### Key Configuration Options

```env
# Database (SQLite default)
DATABASE_URL=sqlite:///data/stealth_bot.db

# For PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost:5432/stealth_bot

# Trading Configuration
INITIAL_CAPITAL=100000
DEFAULT_POSITION_SIZE=1000
MAX_POSITION_SIZE=5000

# Risk Management
MAX_DAILY_LOSS=5000
MAX_POSITIONS=10
```

## Production Deployment

### Option 1: VPS Deployment (DigitalOcean, Linode, etc.)

1. **Provision Server**
   - Ubuntu 22.04 LTS
   - Minimum 2GB RAM, 2 vCPUs
   - 20GB SSD

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

3. **Clone and Deploy**
```bash
git clone <your-repo>
cd stealth-scan-trader-main
./deploy.sh
```

4. **Setup Nginx Reverse Proxy**
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/stealth-bot

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/stealth-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Setup SSL (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option 2: Cloud Deployment (AWS, GCP, Azure)

**AWS EC2 Deployment:**

1. Launch EC2 instance (t3.medium recommended)
2. Configure security groups (allow ports 80, 443, 8000, 3000)
3. SSH into instance
4. Follow VPS deployment steps above

**Database Options:**
- **Development**: SQLite (default, included)
- **Production**: PostgreSQL via AWS RDS or managed service

## Database Migration

### SQLite to PostgreSQL

1. **Setup PostgreSQL**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE stealth_bot;
CREATE USER stealth_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stealth_bot TO stealth_user;
\q
```

2. **Update Environment**
```bash
DATABASE_URL=postgresql://stealth_user:your_password@localhost:5432/stealth_bot
```

3. **Initialize Database**
```bash
python -c "from backend.database import init_db; init_db()"
```

## Monitoring and Maintenance

### View Logs
```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Application logs (if running locally)
tail -f logs/stealth_bot.log
```

### Database Backup
```bash
# SQLite backup
cp data/stealth_bot.db data/stealth_bot_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump -U stealth_user stealth_bot > backup_$(date +%Y%m%d).sql
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend (should return HTML)
curl http://localhost:3000
```

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Port 8000 already in use: Stop other services
# - Database connection: Check DATABASE_URL
# - Missing dependencies: Rebuild image
```

### Frontend Build Errors
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install

# Clear build cache
rm -rf dist
npm run build
```

### Database Issues
```bash
# Reset database (CAUTION: Deletes all data)
python -c "from backend.database import reset_db; reset_db()"

# Or manually delete
rm data/stealth_bot.db
python -c "from backend.database import init_db; init_db()"
```

## Performance Tuning

### Backend Optimization
- **Workers**: Add `--workers 4` to uvicorn command for parallel processing
- **Database Connection Pool**: Increase `pool_size` in `backend/database/session.py`
- **Caching**: Enable Redis for market data caching

### Frontend Optimization
- **Build Optimization**: Already configured in Vite
- **CDN**: Serve static assets from CDN
- **Lazy Loading**: Implemented in React components

## Security Checklist

- [ ] Change default passwords
- [ ] Configure CORS for production domains only
- [ ] Enable HTTPS/SSL
- [ ] Use strong DATABASE_URL password
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Monitor logs for suspicious activity

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review configuration: `.env` and `docker-compose.yml`
- Database status: `curl http://localhost:8000/api/health`

## Next Steps

After deployment:
1. ✅ Verify all services are running
2. ✅ Check API documentation at `/docs`
3. ✅ Configure risk management settings
4. ✅ Set up monitoring and alerts
5. ✅ Run test scans to verify data flow
6. ✅ Monitor performance metrics

Your STEALTH Bot is now ready for production use!
