#!/usr/bin/env python3
"""
ID Card Preview Debug Script
Checks ID card preview page for DOB verification issues
"""

import os
import re

class IDPreviewDebugger:
    def __init__(self, project_path):
        self.project_path = project_path
        self.issues = []
    
    def check_id_preview_template(self):
        """Check ID preview template for DOB verification setup"""
        template_path = os.path.join(self.project_path, 'templates/ID/preview_card.html')
        
        if not os.path.exists(template_path):
            self.issues.append("ID preview template not found")
            return
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for DOB setup
        checks = {
            'USER_DOB variable': 'window.USER_DOB' in content,
            'Download protection class': 'download-protected' in content,
            'JavaScript file included': 'vehicle_pass_download.js' in content,
            'Download buttons exist': 'download-btn' in content,
            'DOB date format': 'date:"Y-m-d"' in content
        }
        
        for check, passed in checks.items():
            if not passed:
                self.issues.append(f"ID Preview: Missing {check}")
    
    def check_js_file_coverage(self):
        """Check if JS file covers ID preview URLs"""
        js_path = os.path.join(self.project_path, 'static/js/vehicle_pass_download.js')
        
        if not os.path.exists(js_path):
            self.issues.append("JavaScript file not found")
            return
        
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for ID preview URL patterns
        id_patterns = [
            '/id/preview/',
            '/id-card/preview/',
            'id-card-btn'
        ]
        
        for pattern in id_patterns:
            if pattern not in content:
                self.issues.append(f"JS file missing pattern: {pattern}")
    
    def check_url_patterns(self):
        """Check URL patterns in Django"""
        url_files = [
            'ID/urls.py',
            'urls.py'
        ]
        
        for url_file in url_files:
            file_path = os.path.join(self.project_path, url_file)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'preview' in content:
                    print(f"Found preview URLs in {url_file}")
    
    def generate_fix_suggestions(self):
        """Generate fix suggestions"""
        fixes = []
        
        if any('Missing USER_DOB' in issue for issue in self.issues):
            fixes.append("Add: window.USER_DOB = '{{ registration.date_of_birth|date:\"Y-m-d\" }}';")
        
        if any('Missing Download protection' in issue for issue in self.issues):
            fixes.append("Add class 'download-protected' to download buttons")
        
        if any('Missing JavaScript' in issue for issue in self.issues):
            fixes.append("Include: <script src=\"/static/js/vehicle_pass_download.js\"></script>")
        
        return fixes
    
    def run_diagnosis(self):
        """Run complete diagnosis"""
        print("🔍 Diagnosing ID card preview DOB verification...")
        
        self.check_id_preview_template()
        self.check_js_file_coverage()
        self.check_url_patterns()
        
        if self.issues:
            print("❌ Issues found:")
            for issue in self.issues:
                print(f"  - {issue}")
            
            print("\n🔧 Suggested fixes:")
            fixes = self.generate_fix_suggestions()
            for fix in fixes:
                print(f"  - {fix}")
        else:
            print("✅ ID preview DOB verification setup looks correct")
        
        print(f"\n📋 Test URL: http://127.0.0.1:8000/id/preview/3324/")
        print("Expected behavior: DOB verification required before download")

if __name__ == "__main__":
    debugger = IDPreviewDebugger("e:/Divy/Projects/GitHub/ycsmp")
    debugger.run_diagnosis()