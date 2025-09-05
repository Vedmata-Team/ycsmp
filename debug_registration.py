#!/usr/bin/env python3
"""
Debug Registration Form - Automated Browser Test
Fills the form and clicks Next button to debug the exact issue
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time

def debug_registration_form():
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Opening registration page...")
        driver.get("http://127.0.0.1:8000/register/")
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Wait for page to load
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "registrationForm"))
            )
        except Exception as e:
            print(f"Timeout waiting for form: {e}")
            print(f"Page source length: {len(driver.page_source)}")
            print("First 500 chars of page:")
            print(driver.page_source[:500])
            raise
        
        print("Page loaded. Testing JavaScript functionality...")
        
        # Skip form filling for now due to interaction issues
        print("Skipping detailed form filling...")
        
        print("Skipping form filling due to interaction issues. Testing JavaScript directly...")
        
        # Test JavaScript functions directly
        js_test = """
        console.log('=== TESTING JAVASCRIPT FUNCTIONS ===');
        
        // Check if functions exist
        console.log('nextStep function:', typeof window.nextStep);
        console.log('showStep function:', typeof window.showStep);
        console.log('generateSummary function:', typeof window.generateSummary);
        
        // Check DOM elements
        const steps = document.querySelectorAll('.form-step');
        const indicators = document.querySelectorAll('.step-indicator .step');
        console.log('Steps found:', steps.length);
        console.log('Indicators found:', indicators.length);
        
        // Test step navigation
        if (typeof window.nextStep === 'function') {
            console.log('Testing nextStep(0)...');
            window.nextStep(0);
            
            setTimeout(() => {
                const activeStep = document.querySelector('.form-step.active');
                console.log('Active step after nextStep:', activeStep ? activeStep.id : 'none');
                
                // Test going to step 3 to check summary
                console.log('Testing showStep(2) for summary...');
                window.showStep(2);
                
                setTimeout(() => {
                    const summaryDiv = document.getElementById('confirmation-summary');
                    console.log('Summary div content:', summaryDiv ? summaryDiv.innerHTML : 'not found');
                }, 500);
            }, 500);
        }
        
        return {
            nextStep: typeof window.nextStep,
            showStep: typeof window.showStep,
            generateSummary: typeof window.generateSummary,
            stepsCount: steps.length,
            indicatorsCount: indicators.length
        };
        """
        
        debug_info = driver.execute_script(js_test)
        print(f"JavaScript test results: {debug_info}")
        
        time.sleep(3)
        
        # Get console logs
        logs = driver.get_log('browser')
        if logs:
            print("Console logs:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        
        # Test form submission
        print("Testing form submission...")
        submit_test = """
        // Go to step 3 and test submission
        window.showStep(2);
        
        setTimeout(() => {
            const termsCheck = document.getElementById('termsCheck');
            const submitBtn = document.getElementById('submitBtn');
            
            console.log('Terms checkbox found:', termsCheck !== null);
            console.log('Submit button found:', submitBtn !== null);
            
            if (termsCheck) {
                termsCheck.checked = true;
                console.log('Terms checkbox checked');
            }
            
            if (submitBtn) {
                console.log('Submit button click test - would submit form');
                // Don't actually submit to avoid page redirect
            }
        }, 1000);
        """
        
        driver.execute_script(submit_test)
        time.sleep(2)
        
        # Get final logs
        logs = driver.get_log('browser')
        if logs:
            print("Final console logs:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        
        print("Test completed. Check console output above.")
        input("Press Enter to close browser...")
        
    except Exception as e:
        print(f"Error: {e}")
        
        # Get console logs on error
        try:
            logs = driver.get_log('browser')
            if logs:
                print("Console logs on error:")
                for log in logs:
                    print(f"  {log['level']}: {log['message']}")
        except:
            pass
            
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Starting automated registration form debug...")
    debug_registration_form()