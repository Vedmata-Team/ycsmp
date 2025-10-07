#!/usr/bin/env python3
"""
Comprehensive test for bulk email system - all scenarios
Tests streaming, console output, email sending, and error handling
"""

import os
import sys
import django
import time
import requests
from io import StringIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

from events.models import EventRegistration
from events.email_utils import send_registration_approval_email
from events.streaming_views import stream_bulk_email
from django.test import RequestFactory, Client
from django.contrib.auth.models import User

class BulkEmailTester:
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.test_results = []
        
    def log_test(self, test_name, success, message):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append((test_name, success, message))
    
    def test_1_email_system_basic(self):
        """Test basic email system functionality"""
        print("\n🧪 Test 1: Basic Email System")
        print("-" * 40)
        
        try:
            # Find test registration
            reg = EventRegistration.objects.filter(
                approval_status='approved',
                email__isnull=False
            ).exclude(email='').first()
            
            if not reg:
                self.log_test("Basic Email", False, "No test registration found")
                return False
            
            print(f"Testing with: {reg.full_name} ({reg.email})")
            
            # Test simple email
            start_time = time.time()
            success = send_registration_approval_email(reg, skip_attachments=True)
            elapsed = time.time() - start_time
            
            if success and elapsed < 5.0:
                self.log_test("Basic Email", True, f"Sent in {elapsed:.2f}s")
                return True
            else:
                self.log_test("Basic Email", False, f"Failed or too slow ({elapsed:.2f}s)")
                return False
                
        except Exception as e:
            self.log_test("Basic Email", False, f"Exception: {str(e)}")
            return False
    
    def test_2_console_output_capture(self):
        """Test console output capture"""
        print("\n🧪 Test 2: Console Output Capture")
        print("-" * 40)
        
        try:
            # Capture stdout
            old_stdout = sys.stdout
            captured_output = StringIO()
            sys.stdout = captured_output
            
            # Send test email
            reg = EventRegistration.objects.filter(approval_status='approved').first()
            send_registration_approval_email(reg, skip_attachments=True)
            
            # Get captured output
            console_output = captured_output.getvalue()
            sys.stdout = old_stdout
            
            if console_output and "ULTRA-FAST EMAIL SYSTEM" in console_output:
                self.log_test("Console Capture", True, f"Captured {len(console_output)} chars")
                print(f"Sample output: {console_output[:100]}...")
                return True
            else:
                self.log_test("Console Capture", False, "No output captured")
                return False
                
        except Exception as e:
            sys.stdout = old_stdout
            self.log_test("Console Capture", False, f"Exception: {str(e)}")
            return False
    
    def test_3_streaming_endpoint(self):
        """Test streaming endpoint"""
        print("\n🧪 Test 3: Streaming Endpoint")
        print("-" * 40)
        
        try:
            # Get test registrations
            regs = EventRegistration.objects.filter(approval_status='approved')[:2]
            if not regs:
                self.log_test("Streaming Endpoint", False, "No test registrations")
                return False
            
            reg_ids = [str(reg.id) for reg in regs]
            
            # Create superuser for test
            user, created = User.objects.get_or_create(
                username='test_admin',
                defaults={'is_staff': True, 'is_superuser': True}
            )
            
            # Test streaming view
            request = self.factory.get(f'/stream-bulk-email/?ids={",".join(reg_ids)}')
            request.user = user
            
            response = stream_bulk_email(request)
            
            if response.status_code == 200:
                self.log_test("Streaming Endpoint", True, "Endpoint accessible")
                return True
            else:
                self.log_test("Streaming Endpoint", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Streaming Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_4_bulk_processing_simulation(self):
        """Test bulk processing with multiple emails"""
        print("\n🧪 Test 4: Bulk Processing Simulation")
        print("-" * 40)
        
        try:
            # Get 3 test registrations
            regs = list(EventRegistration.objects.filter(approval_status='approved')[:3])
            if len(regs) < 2:
                self.log_test("Bulk Processing", False, "Need at least 2 registrations")
                return False
            
            print(f"Testing bulk processing with {len(regs)} registrations")
            
            success_count = 0
            total_time = 0
            
            for i, reg in enumerate(regs):
                print(f"Processing {i+1}/{len(regs)}: {reg.full_name}")
                
                start_time = time.time()
                success = send_registration_approval_email(reg, skip_attachments=True)
                elapsed = time.time() - start_time
                total_time += elapsed
                
                if success:
                    success_count += 1
                    print(f"  ✅ Success in {elapsed:.2f}s")
                else:
                    print(f"  ❌ Failed in {elapsed:.2f}s")
                
                # Small delay like real system
                time.sleep(0.5)
            
            avg_time = total_time / len(regs)
            success_rate = (success_count / len(regs)) * 100
            
            if success_rate >= 80 and avg_time < 5.0:
                self.log_test("Bulk Processing", True, f"{success_rate:.0f}% success, {avg_time:.2f}s avg")
                return True
            else:
                self.log_test("Bulk Processing", False, f"{success_rate:.0f}% success, {avg_time:.2f}s avg")
                return False
                
        except Exception as e:
            self.log_test("Bulk Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_5_error_handling(self):
        """Test error handling scenarios"""
        print("\n🧪 Test 5: Error Handling")
        print("-" * 40)
        
        try:
            # Test with invalid registration
            from events.models import EventRegistration
            
            # Create a test registration with invalid email
            reg = EventRegistration.objects.filter(approval_status='approved').first()
            if not reg:
                self.log_test("Error Handling", False, "No test registration")
                return False
            
            # Backup original email
            original_email = reg.email
            
            # Test with invalid email
            reg.email = "invalid-email-test@nonexistent-domain-12345.com"
            
            success = send_registration_approval_email(reg, skip_attachments=True)
            
            # Restore original email
            reg.email = original_email
            
            # Should fail gracefully
            if not success:
                self.log_test("Error Handling", True, "Gracefully handled invalid email")
                return True
            else:
                self.log_test("Error Handling", False, "Should have failed with invalid email")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", True, f"Exception caught: {str(e)[:50]}...")
            return True
    
    def test_6_javascript_compatibility(self):
        """Test JavaScript file exists and has required functions"""
        print("\n🧪 Test 6: JavaScript Compatibility")
        print("-" * 40)
        
        try:
            js_file = "static/admin/js/bulk_email_sender.js"
            
            if not os.path.exists(js_file):
                self.log_test("JavaScript File", False, "File not found")
                return False
            
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_functions = [
                'startRealTimeStream',
                'EventSource',
                'updateBulkProgress',
                'showBulkProgress'
            ]
            
            missing = []
            for func in required_functions:
                if func not in content:
                    missing.append(func)
            
            if not missing:
                self.log_test("JavaScript File", True, "All required functions found")
                return True
            else:
                self.log_test("JavaScript File", False, f"Missing: {', '.join(missing)}")
                return False
                
        except Exception as e:
            self.log_test("JavaScript File", False, f"Exception: {str(e)}")
            return False
    
    def test_7_performance_benchmark(self):
        """Performance benchmark test"""
        print("\n🧪 Test 7: Performance Benchmark")
        print("-" * 40)
        
        try:
            reg = EventRegistration.objects.filter(approval_status='approved').first()
            if not reg:
                self.log_test("Performance", False, "No test registration")
                return False
            
            # Test multiple runs
            times = []
            for i in range(3):
                start_time = time.time()
                success = send_registration_approval_email(reg, skip_attachments=True)
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                if not success:
                    self.log_test("Performance", False, f"Failed on run {i+1}")
                    return False
                
                time.sleep(1)  # Delay between tests
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"Times: {[f'{t:.2f}s' for t in times]}")
            print(f"Average: {avg_time:.2f}s, Min: {min_time:.2f}s, Max: {max_time:.2f}s")
            
            if avg_time < 3.0 and max_time < 5.0:
                self.log_test("Performance", True, f"Avg: {avg_time:.2f}s, Max: {max_time:.2f}s")
                return True
            else:
                self.log_test("Performance", False, f"Too slow - Avg: {avg_time:.2f}s")
                return False
                
        except Exception as e:
            self.log_test("Performance", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Bulk Email System - Comprehensive Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_1_email_system_basic,
            self.test_2_console_output_capture,
            self.test_3_streaming_endpoint,
            self.test_4_bulk_processing_simulation,
            self.test_5_error_handling,
            self.test_6_javascript_compatibility,
            self.test_7_performance_benchmark
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
        
        # Generate final report
        print("\n" + "=" * 60)
        print("📊 Final Test Report")
        print("=" * 60)
        
        for test_name, success, message in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}: {message}")
        
        print(f"\n📈 Overall Result: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! System is ready for production.")
            return True
        elif passed >= total * 0.8:
            print("⚠️ Most tests passed. Review failed tests before going live.")
            return False
        else:
            print("❌ Multiple test failures. System needs fixes before production.")
            return False

def main():
    """Main test runner"""
    tester = BulkEmailTester()
    success = tester.run_all_tests()
    
    print(f"\n{'='*60}")
    if success:
        print("🟢 SYSTEM READY FOR PRODUCTION")
    else:
        print("🔴 SYSTEM NEEDS FIXES")
    print("="*60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)