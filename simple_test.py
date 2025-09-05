#!/usr/bin/env python3
"""
Simple test to check if registration page loads and JavaScript works
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def simple_test():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless for faster testing
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Loading page...")
        driver.set_page_load_timeout(10)
        driver.get("http://127.0.0.1:8000/register/")
        
        print(f"Page title: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        # Check if form exists
        form = driver.find_element(By.ID, "registrationForm")
        print(f"Form found: {form is not None}")
        
        # Check JavaScript functions
        js_result = driver.execute_script("""
            return {
                nextStep: typeof window.nextStep,
                prevStep: typeof window.prevStep,
                showStep: typeof window.showStep,
                stepsCount: document.querySelectorAll('.form-step').length,
                jsLoaded: document.querySelector('script[src*="registration_form.js"]') !== null
            };
        """)
        
        print(f"JavaScript check: {js_result}")
        
        # Get console logs
        logs = driver.get_log('browser')
        if logs:
            print("Console logs:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        else:
            print("No console logs")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    simple_test()