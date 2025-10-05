#!/usr/bin/env python3
"""
Test Button Click Functionality
Creates a simple HTML test page to debug button clicks
"""

def create_test_html():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Button Click Test</title>
    <script>
        // Test DOB verification
        window.USER_DOB = '1990-01-15';
        
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded');
            
            const verifyBtn = document.getElementById('verifyDOB');
            if (verifyBtn) {
                console.log('Verify button found');
                verifyBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Button clicked!');
                    
                    const dobInput = document.getElementById('dobInput');
                    const inputValue = dobInput.value;
                    console.log('DOB input value:', inputValue);
                    
                    if (inputValue === '1990-01-15') {
                        console.log('DOB matches - should download');
                        alert('Success! DOB verified');
                    } else {
                        console.log('DOB does not match');
                        alert('Incorrect DOB');
                    }
                });
            } else {
                console.log('Verify button NOT found');
            }
        });
    </script>
</head>
<body>
    <h1>Button Click Test</h1>
    <div>
        <label>Date of Birth:</label>
        <input type="date" id="dobInput" value="1990-01-15">
    </div>
    <br>
    <button id="verifyDOB">Verify & Download</button>
    
    <script>
        console.log('Script loaded');
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    with open("test_button.html", "w") as f:
        f.write(create_test_html())
    print("Created test_button.html - Open in browser to test button clicks")