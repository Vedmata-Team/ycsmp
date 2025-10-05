// Debug script to test button functionality
console.log('Debug script loaded');

// Test if USER_DOB is available
console.log('USER_DOB:', window.USER_DOB);

// Add test button functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded for debug');
    
    // Find verify button
    setTimeout(() => {
        const verifyBtn = document.getElementById('verifyDOB');
        if (verifyBtn) {
            console.log('Verify button found in debug');
            
            // Add test click handler
            verifyBtn.addEventListener('click', function(e) {
                console.log('DEBUG: Button clicked!');
                e.preventDefault();
                
                const dobInput = document.getElementById('dobInput');
                if (dobInput) {
                    console.log('DEBUG: DOB input value:', dobInput.value);
                    console.log('DEBUG: Expected DOB:', window.USER_DOB);
                    
                    if (dobInput.value) {
                        alert('Button is working! DOB entered: ' + dobInput.value);
                    } else {
                        alert('Please enter a date of birth');
                    }
                }
            });
        } else {
            console.log('Verify button NOT found in debug');
        }
    }, 1000);
});