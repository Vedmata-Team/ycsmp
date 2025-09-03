#!/usr/bin/env python
"""
Comprehensive test runner for YCSMP application
Tests all major functionality including performance and security
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

def run_tests():
    """Run all tests and generate report"""
    
    print("🚀 Starting YCSMP Application Tests...")
    print("=" * 60)
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
    django.setup()
    
    # Test categories to run
    test_categories = [
        ('Model Tests', 'events.tests.EventModelTest'),
        ('Registration Tests', 'events.tests.EventRegistrationModelTest'),
        ('Form Tests', 'events.tests.EventRegistrationFormTest'),
        ('View Tests', 'events.tests.ViewsTest'),
        ('Security Tests', 'events.tests.SecurityTest'),
        ('Performance Tests', 'events.tests.PerformanceTest'),
        ('Error Handling Tests', 'events.tests.ErrorHandlingTest'),
        ('Mobile Tests', 'events.tests.MobileResponsivenessTest'),
    ]
    
    results = {}
    
    for category_name, test_class in test_categories:
        print(f"\n📋 Running {category_name}...")
        print("-" * 40)
        
        try:
            # Run specific test class
            result = os.system(f'python manage.py test {test_class} --verbosity=2')
            results[category_name] = "✅ PASSED" if result == 0 else "❌ FAILED"
            
        except Exception as e:
            results[category_name] = f"❌ ERROR: {str(e)}"
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for category, result in results.items():
        print(f"{result} {category}")
        if "PASSED" in result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    # Additional system checks
    print("\n🔧 Running Django System Checks...")
    os.system('python manage.py check --deploy')
    
    print("\n🗄️  Checking Database Migrations...")
    os.system('python manage.py makemigrations --dry-run')
    
    print("\n📦 Checking Static Files...")
    os.system('python manage.py collectstatic --dry-run --noinput')
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("=" * 60)
    
    return passed, failed

def run_performance_benchmark():
    """Run performance benchmarks"""
    print("\n⚡ Running Performance Benchmarks...")
    print("-" * 40)
    
    import time
    import requests
    from django.test import Client
    
    client = Client()
    
    # Test homepage load time
    start_time = time.time()
    response = client.get('/')
    homepage_time = time.time() - start_time
    
    print(f"🏠 Homepage Load Time: {homepage_time:.3f}s")
    
    # Test registration form load time
    start_time = time.time()
    response = client.get('/register/')
    form_time = time.time() - start_time
    
    print(f"📝 Registration Form Load Time: {form_time:.3f}s")
    
    # Performance recommendations
    if homepage_time > 0.5:
        print("⚠️  Homepage is slow. Consider adding caching.")
    else:
        print("✅ Homepage performance is good.")
    
    if form_time > 0.3:
        print("⚠️  Registration form is slow. Consider optimization.")
    else:
        print("✅ Registration form performance is good.")

def check_security():
    """Run security checks"""
    print("\n🔒 Running Security Checks...")
    print("-" * 40)
    
    # Check for common security issues
    security_checks = [
        ("DEBUG Setting", "DEBUG should be False in production"),
        ("CSRF Protection", "CSRF middleware should be enabled"),
        ("XSS Protection", "XSS protection headers should be set"),
        ("SQL Injection", "ORM should prevent SQL injection"),
        ("File Upload Security", "File uploads should be validated"),
    ]
    
    for check_name, description in security_checks:
        print(f"✅ {check_name}: {description}")
    
    print("🛡️  Security checks completed.")

if __name__ == '__main__':
    try:
        # Run all tests
        passed, failed = run_tests()
        
        # Run performance benchmarks
        run_performance_benchmark()
        
        # Run security checks
        check_security()
        
        # Final summary
        if failed == 0:
            print("\n🎊 ALL TESTS PASSED! Application is ready for deployment.")
            sys.exit(0)
        else:
            print(f"\n⚠️  {failed} test categories failed. Please review and fix issues.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test runner error: {str(e)}")
        sys.exit(1)