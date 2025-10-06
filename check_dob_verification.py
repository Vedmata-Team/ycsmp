#!/usr/bin/env python3
"""
DOB Verification Checker
Tests DOB verification across all user types and pages
"""

import os
import re

class DOBVerificationChecker:
    def __init__(self, project_path):
        self.project_path = project_path
        self.issues = []
        self.pages_checked = []
    
    def check_template_dob_setup(self, template_path, page_name):
        """Check if template has proper DOB verification setup"""
        if not os.path.exists(template_path):
            self.issues.append(f"{page_name}: Template not found")
            return False
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'USER_DOB variable': 'window.USER_DOB' in content,
            'DOB date format': 'date:"Y-m-d"' in content or 'date:\"Y-m-d\"' in content,
            'JavaScript file': 'vehicle_pass_download.js' in content,
            'Protected elements': 'download-protected' in content or 'download-btn' in content
        }
        
        page_status = {'name': page_name, 'checks': checks, 'issues': []}
        
        for check, passed in checks.items():
            if not passed:
                page_status['issues'].append(f"Missing {check}")
                self.issues.append(f"{page_name}: Missing {check}")
        
        self.pages_checked.append(page_status)
        return len(page_status['issues']) == 0
    
    def check_all_pages(self):
        """Check DOB verification on all relevant pages"""
        pages_to_check = [
            ('templates/vehicle_pass/vehicle_pass_preview.html', 'Vehicle Pass Preview'),
            ('templates/ID/preview_card.html', 'ID Card Preview'),
            ('templates/events/registration_profile.html', 'Profile Page'),
            ('templates/admin/vehicle_pass_download.html', 'Admin Download')
        ]
        
        for template_path, page_name in pages_to_check:
            full_path = os.path.join(self.project_path, template_path)
            self.check_template_dob_setup(full_path, page_name)
    
    def check_js_coverage(self):
        """Check JavaScript file for comprehensive coverage"""
        js_path = os.path.join(self.project_path, 'static/js/vehicle_pass_download.js')
        
        if not os.path.exists(js_path):
            self.issues.append("JavaScript file not found")
            return
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for all URL patterns
        required_patterns = [
            '/vehicle-pass/generate/',
            '/id/card/',
            '/vehicle-pass/preview/',
            '/id/preview/',
            'download-protected',
            'validateDOB'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            self.issues.append(f"JS missing patterns: {', '.join(missing_patterns)}")
    
    def check_user_types(self):
        """Check if DOB verification works for different user types"""
        user_types = ['participant', 'volunteer', 'organization_representative']
        
        # Check if templates handle different user types
        profile_path = os.path.join(self.project_path, 'templates/events/registration_profile.html')
        if os.path.exists(profile_path):
            with open(profile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for user_type in user_types:
                if user_type not in content:
                    self.issues.append(f"Profile template may not handle {user_type} users")
    
    def generate_test_scenarios(self):
        """Generate test scenarios for different user types"""
        scenarios = [
            {
                'user_type': 'participant',
                'test_urls': [
                    'http://127.0.0.1:8000/profile/9575726041_Ravindra_Singh_Jamra/view/',
                    'http://127.0.0.1:8000/id/preview/3324/',
                    'http://127.0.0.1:8000/vehicle-pass/preview/3324/MP69C1216/'
                ],
                'expected': 'DOB verification required for all actions'
            },
            {
                'user_type': 'volunteer',
                'test_urls': [
                    'Profile page with volunteer type',
                    'ID card download',
                    'Vehicle pass download'
                ],
                'expected': 'Same DOB verification for volunteers'
            },
            {
                'user_type': 'organization_representative',
                'test_urls': [
                    'Profile page with org rep type',
                    'ID card download',
                    'Vehicle pass download'
                ],
                'expected': 'Same DOB verification for org reps'
            }
        ]
        return scenarios
    
    def run_comprehensive_check(self):
        """Run complete DOB verification check"""
        print("🔍 Checking DOB verification across all user types and pages...")
        
        self.check_all_pages()
        self.check_js_coverage()
        self.check_user_types()
        
        print(f"\n📊 Pages Checked: {len(self.pages_checked)}")
        for page in self.pages_checked:
            status = "✅" if len(page['issues']) == 0 else "❌"
            print(f"{status} {page['name']}")
            for issue in page['issues']:
                print(f"    - {issue}")
        
        if self.issues:
            print(f"\n❌ Total Issues Found: {len(self.issues)}")
            for issue in self.issues:
                print(f"  - {issue}")
        else:
            print("\n✅ All DOB verification checks passed!")
        
        print("\n🧪 Test Scenarios:")
        scenarios = self.generate_test_scenarios()
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. {scenario['user_type'].title()} User:")
            print(f"   Expected: {scenario['expected']}")
            for url in scenario['test_urls']:
                print(f"   Test: {url}")
        
        print(f"\n📋 Test DOB: 1995-12-04 (if USER_DOB not set)")
        print("Expected behavior: DOB verification modal → Enter correct DOB → Access granted")

if __name__ == "__main__":
    checker = DOBVerificationChecker("e:/Divy/Projects/GitHub/ycsmp")
    checker.run_comprehensive_check()