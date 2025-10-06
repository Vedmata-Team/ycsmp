#!/usr/bin/env python3
"""
Email Server Connection Test
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')

try:
    import django
    django.setup()
    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Django setup failed: {e}")
    print("Running basic SMTP test only...")
    DJANGO_AVAILABLE = False

import smtplib
import socket

if DJANGO_AVAILABLE:
    from django.conf import settings
    from django.core.mail import send_mail, get_connection
else:
    # Fallback settings for basic testing (Office365)
    class MockSettings:
        EMAIL_HOST = 'smtp.office365.com'
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True
        EMAIL_USE_SSL = False
        EMAIL_HOST_USER = 'youthcell@awgp.org'
        EMAIL_HOST_PASSWORD = 'PpgPvm@24'
        DEFAULT_FROM_EMAIL = 'youthcell@awgp.org'
    settings = MockSettings()

def test_email_settings():
    print("🔍 EMAIL SETTINGS TEST")
    print("=" * 50)
    
    # Check email settings
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    print()

def test_smtp_connection():
    print("🔍 SMTP CONNECTION TEST")
    print("=" * 50)
    
    try:
        host = getattr(settings, 'EMAIL_HOST', '')
        port = getattr(settings, 'EMAIL_PORT', 587)
        use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
        use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
        username = getattr(settings, 'EMAIL_HOST_USER', '')
        password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        
        print(f"Testing connection to {host}:{port}")
        
        # Test socket connection first
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            print(f"❌ Cannot connect to {host}:{port} - Network/firewall issue")
            return False
        else:
            print(f"✅ Socket connection to {host}:{port} successful")
        
        # Test SMTP connection
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
        else:
            server = smtplib.SMTP(host, port, timeout=10)
            if use_tls:
                server.starttls()
        
        if username and password:
            server.login(username, password)
            print("✅ SMTP authentication successful")
        
        server.quit()
        print("✅ SMTP connection test successful")
        return True
        
    except socket.timeout:
        print("❌ Connection timeout - Server may be down or blocked")
        return False
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP authentication failed - Check username/password")
        return False
    except smtplib.SMTPConnectError:
        print("❌ SMTP connection failed - Server refused connection")
        return False
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def test_django_email():
    if not DJANGO_AVAILABLE:
        print("⚠️ Skipping Django email test - Django not available")
        return True
        
    print("🔍 DJANGO EMAIL TEST")
    print("=" * 50)
    
    try:
        # Test Django email connection
        connection = get_connection()
        connection.timeout = 10
        connection.open()
        print("✅ Django email connection successful")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Django email connection failed: {e}")
        return False

def test_send_email():
    if not DJANGO_AVAILABLE:
        print("⚠️ Skipping Django email send test - Django not available")
        return True
        
    print("🔍 TEST EMAIL SEND")
    print("=" * 50)
    
    try:
        test_email = input("Enter test email address (or press Enter to skip): ").strip()
        if not test_email:
            print("⏭️ Skipping email send test")
            return True
            
        send_mail(
            subject='YCSMP Email Test',
            message='This is a test email from YCSMP system.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print(f"✅ Test email sent successfully to {test_email}")
        return True
    except Exception as e:
        print(f"❌ Test email failed: {e}")
        return False

def suggest_fixes():
    print("\n🔧 SUGGESTED FIXES")
    print("=" * 50)
    print("1. Check internet connection")
    print("2. Verify SMTP server settings in settings.py")
    print("3. Check if firewall is blocking SMTP ports (587, 465, 25)")
    print("4. Verify email credentials are correct")
    print("5. Try using Gmail SMTP for testing:")
    print("   EMAIL_HOST = 'smtp.gmail.com'")
    print("   EMAIL_PORT = 587")
    print("   EMAIL_USE_TLS = True")
    print("6. For Gmail, use App Password instead of regular password")

if __name__ == "__main__":
    test_email_settings()
    smtp_ok = test_smtp_connection()
    django_ok = test_django_email()
    
    if smtp_ok and django_ok:
        test_send_email()
    else:
        suggest_fixes()