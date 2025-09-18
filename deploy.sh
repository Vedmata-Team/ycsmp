# YCSMP Deployment Script - One-shot command for git pull, collectstatic, and restart
echo "🚀 Starting YCSMP deployment..."

# Navigate to project directory
cd /home/divy/myproject/ycsmp

# Activate virtual environment
source venv/bin/activate

# Git pull latest changes
echo "📥 Pulling latest changes from Git..."
git pull origin main

# Collect static files (no input required)Mohan123#

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Restart Gunicorn service
echo "🔄 Restarting Gunicorn service..."
sudo systemctl restart ycsmp.service

# Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

# Check service status
echo "✅ Checking service status..."
sudo systemctl status ycsmp.service --no-pager -l
sudo systemctl status nginx --no-pager -l

echo "🎉 Deployment completed successfully!"
echo "🌐 Website: https://ycsmp.in"
