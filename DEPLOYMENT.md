# 🚀 YCSMP Production Deployment Guide

## 📋 Prerequisites

1. **Server Requirements:**
   - Ubuntu 20.04+ or CentOS 8+
   - Python 3.8+
   - PostgreSQL 12+
   - Redis 6+ (optional but recommended)
   - Nginx

2. **Domain Setup:**
   - Point `ycsmp.in` and `www.ycsmp.in` to your server IP
   - SSL certificate (Let's Encrypt recommended)

## 🔧 Quick Deployment Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Create project user
sudo useradd -m -s /bin/bash ycsmp
sudo usermod -aG sudo ycsmp
```

### 2. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE ycsmp_db;
CREATE USER ycsmp_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ycsmp_db TO ycsmp_user;
\q
```

### 3. Project Deployment
```bash
# Switch to project user
sudo su - ycsmp

# Clone project
git clone https://github.com/your-username/ycsmp.git
cd ycsmp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Create .env file
cp .env.example .env
# Edit .env with your production values

# Run deployment script
python deploy.py
```

### 4. Web Server Configuration
```bash
# Copy Nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/ycsmp
sudo ln -s /etc/nginx/sites-available/ycsmp /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Process Management
```bash
# Create systemd service for Gunicorn
sudo nano /etc/systemd/system/ycsmp.service
```

Add this content:
```ini
[Unit]
Description=YCSMP Gunicorn daemon
After=network.target

[Service]
User=ycsmp
Group=www-data
WorkingDirectory=/home/ycsmp/ycsmp
ExecStart=/home/ycsmp/ycsmp/venv/bin/gunicorn --config gunicorn.conf.py ycs_mp.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start services
sudo systemctl daemon-reload
sudo systemctl start ycsmp
sudo systemctl enable ycsmp
sudo systemctl status ycsmp
```

## 🔒 Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure SSL certificate
- [ ] Set up firewall (UFW)
- [ ] Enable fail2ban
- [ ] Regular backups configured
- [ ] Monitor logs

## 📊 Monitoring

### Log Locations:
- Django: `/var/log/gunicorn/ycsmp_error.log`
- Nginx: `/var/log/nginx/error.log`
- System: `journalctl -u ycsmp`

### Health Check:
```bash
# Check services
sudo systemctl status ycsmp nginx postgresql redis

# Test application
curl -I https://ycsmp.in
```

## 🔄 Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart ycsmp
```

## 🆘 Troubleshooting

### Common Issues:

1. **Static files not loading:**
   ```bash
   python manage.py collectstatic --noinput
   sudo systemctl restart nginx
   ```

2. **Database connection error:**
   - Check PostgreSQL is running
   - Verify database credentials in `.env`

3. **Permission errors:**
   ```bash
   sudo chown -R ycsmp:www-data /home/ycsmp/ycsmp
   sudo chmod -R 755 /home/ycsmp/ycsmp
   ```

## 📞 Support

For deployment issues, check:
- Application logs: `tail -f /var/log/gunicorn/ycsmp_error.log`
- System logs: `journalctl -u ycsmp -f`
- Nginx logs: `tail -f /var/log/nginx/error.log`