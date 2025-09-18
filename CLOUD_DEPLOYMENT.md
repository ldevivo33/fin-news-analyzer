# Cloud Deployment Guide

This guide explains how to deploy the Financial News Sentiment Analyzer to AWS EC2 or other cloud platforms.

## Prerequisites

- Python 3.11+
- pip
- Git
- (Optional) Docker and Docker Compose

## Quick Start

### 1. Environment Setup

Copy the example configuration file:
```bash
cp config.env.example .env
```

Edit `.env` with your desired settings:
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# CORS Configuration
ALLOWED_ORIGINS=*

# Database Configuration
DB_TYPE=sqlite
DB_NAME=finnews
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Application

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Manual start:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## AWS EC2 Deployment

### 1. Launch EC2 Instance

- Choose Ubuntu 22.04 LTS or Amazon Linux 2
- Instance type: t3.medium or larger (for ML model loading)
- Security Group: Allow inbound traffic on port 8000 (or your chosen port)
- Storage: At least 20GB

### 2. Connect and Setup

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install additional dependencies
sudo apt install curl git build-essential -y
```

### 3. Deploy Application

```bash
# Clone your repository
git clone https://github.com/your-username/fin-news-analyzer.git
cd fin-news-analyzer

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HOST=0.0.0.0
export PORT=8000
export DEBUG=false
export LOG_LEVEL=INFO

# Start the application
./start.sh
```

### 4. Configure Security Group

In AWS Console:
1. Go to EC2 → Security Groups
2. Edit inbound rules
3. Add rule: Type=Custom TCP, Port=8000, Source=0.0.0.0/0

### 5. Access Your Application

Open your browser and navigate to:
```
http://your-ec2-public-ip:8000
```

## Docker Deployment

### 1. Build and Run with Docker

```bash
# Build the image
docker build -t fin-news-analyzer .

# Run the container
docker run -p 8000:8000 fin-news-analyzer
```

### 2. Use Docker Compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins (comma-separated) |
| `DB_TYPE` | `sqlite` | Database type (sqlite, postgresql, mysql) |
| `DB_NAME` | `finnews` | Database name |
| `DB_HOST` | - | Database host (for PostgreSQL/MySQL) |
| `DB_PORT` | - | Database port (for PostgreSQL/MySQL) |
| `DB_USER` | - | Database username (for PostgreSQL/MySQL) |
| `DB_PASSWORD` | - | Database password (for PostgreSQL/MySQL) |
| `DB_ECHO` | `false` | Enable SQL query logging |

## Database Configuration

### SQLite (Default)
No additional configuration needed. Database file will be created in `backend/finnews.db`.

### PostgreSQL
```bash
export DB_TYPE=postgresql
export DB_HOST=your-postgres-host
export DB_PORT=5432
export DB_NAME=finnews
export DB_USER=your-username
export DB_PASSWORD=your-password
```

### MySQL
```bash
export DB_TYPE=mysql
export DB_HOST=your-mysql-host
export DB_PORT=3306
export DB_NAME=finnews
export DB_USER=your-username
export DB_PASSWORD=your-password
```

## Production Considerations

### 1. Process Management

Use a process manager like PM2 or systemd:

**PM2:**
```bash
npm install -g pm2
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name fin-news-analyzer
pm2 save
pm2 startup
```

**Systemd:**
Create `/etc/systemd/system/fin-news-analyzer.service`:
```ini
[Unit]
Description=Financial News Sentiment Analyzer
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fin-news-analyzer
Environment=PATH=/home/ubuntu/fin-news-analyzer/venv/bin
ExecStart=/home/ubuntu/fin-news-analyzer/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Reverse Proxy (Nginx)

Install and configure Nginx:

```bash
sudo apt install nginx -y
```

Create `/etc/nginx/sites-available/fin-news-analyzer`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/fin-news-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Logs

### Application Logs
Logs are written to stdout. For production, consider redirecting to files:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 >> logs/app.log 2>&1
```

### Health Check
The application provides a health check endpoint:
```
GET http://your-server:8000/health
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Permission denied:**
   ```bash
   chmod +x start.sh
   ```

3. **Database connection issues:**
   - Check database credentials
   - Ensure database server is running
   - Verify network connectivity

4. **Model loading issues:**
   - Ensure sufficient memory (at least 2GB RAM)
   - Check internet connection for model downloads
   - Verify Python dependencies are installed

### Logs

Check application logs for detailed error information:
```bash
# If using PM2
pm2 logs fin-news-analyzer

# If using systemd
sudo journalctl -u fin-news-analyzer -f

# If running directly
tail -f logs/app.log
```

## Scaling

For high-traffic deployments:

1. **Load Balancer:** Use AWS Application Load Balancer or Nginx
2. **Multiple Instances:** Deploy multiple app instances behind a load balancer
3. **Database:** Use managed database services (RDS, Aurora)
4. **Caching:** Implement Redis for caching
5. **CDN:** Use CloudFront for static assets

## Security

1. **Firewall:** Restrict access to necessary ports only
2. **HTTPS:** Always use SSL/TLS in production
3. **Environment Variables:** Never commit sensitive data to version control
4. **Updates:** Keep dependencies and system packages updated
5. **Monitoring:** Implement proper logging and monitoring
