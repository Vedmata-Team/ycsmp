#!/usr/bin/env python3
"""
Production Deployment Script for YCSMP
Run this script to deploy to production server
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("🚀 Starting YCSMP Production Deployment")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please create it from .env.example")
        sys.exit(1)
    
    # Install dependencies
    run_command("pip install -r requirements.txt", "Installing dependencies")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # Run migrations
    run_command("python manage.py migrate", "Running database migrations")
    
    # Create superuser (optional)
    print("\n📝 Create superuser for admin access (optional):")
    subprocess.run("python manage.py createsuperuser", shell=True)
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your web server (Nginx/Apache)")
    print("2. Set up SSL certificate")
    print("3. Configure domain DNS")
    print("4. Start gunicorn: gunicorn ycs_mp.wsgi:application")

if __name__ == "__main__":
    main()