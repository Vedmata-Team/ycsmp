#!/usr/bin/env python3
"""
Button Click Issue Debugger
Analyzes JavaScript files for button click event problems
"""

import os
import re

class ButtonDebugger:
    def __init__(self, project_path):
        self.project_path = project_path
        self.issues = []
    
    def check_js_files(self):
        """Check JavaScript files for button click issues"""
        js_files = [
            'static/js/vehicle_pass_download.js',
            'static/js/dob_verification.js'
        ]
        
        for js_file in js_files:
            file_path = os.path.join(self.project_path, js_file)
            if os.path.exists(file_path):
                self.analyze_js_file(file_path)
    
    def analyze_js_file(self, file_path):
        """Analyze JavaScript file for button issues"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common button issues
        issues = []
        
        # Check for onclick vs addEventListener
        if '.onclick =' in content:
            issues.append("Using .onclick instead of addEventListener")
        
        # Check for missing preventDefault
        if 'addEventListener(' in content and 'preventDefault' not in content:
            issues.append("Missing preventDefault() in event handlers")
        
        # Check for DOM ready issues
        if 'DOMContentLoaded' not in content and 'document.ready' not in content:
            issues.append("No DOM ready check")
        
        # Check for button selectors
        has_button_selectors = (
            'querySelector(' in content and 'btn' in content or
            '#verifyDOB' in content or
            '.dob-verify-btn' in content or
            'getElementById(' in content
        )
        if not has_button_selectors:
            issues.append("No button selectors found")
        
        if issues:
            self.issues.append({
                'file': file_path,
                'issues': issues
            })
    
    def generate_fix_js(self):
        """Generate fixed JavaScript code"""
        return """
// Fixed button event handling
document.addEventListener('DOMContentLoaded', function() {
    const verifyBtn = document.getElementById('verifyDOB');
    if (verifyBtn) {
        verifyBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Button clicked successfully');
            // Your verification logic here
        });
    }
});
"""
    
    def run_diagnosis(self):
        """Run complete button diagnosis"""
        print("🔍 Diagnosing button click issues...")
        self.check_js_files()
        
        if self.issues:
            print("❌ Issues found:")
            for issue in self.issues:
                print(f"File: {issue['file']}")
                for problem in issue['issues']:
                    print(f"  - {problem}")
        else:
            print("✅ No button issues detected")
        
        print("\n🔧 Suggested fix:")
        print(self.generate_fix_js())

if __name__ == "__main__":
    debugger = ButtonDebugger("e:/Divy/Projects/GitHub/ycsmp")
    debugger.run_diagnosis()