// Simple Admin Navigation Fix
// Ensures normal Django admin navigation works without interference

console.log('Admin Navigation Fix loaded');

document.addEventListener('DOMContentLoaded', function() {
    // Clear any problematic localStorage entries
    Object.keys(localStorage).forEach(key => {
        if (key.includes('admin_filters')) {
            localStorage.removeItem(key);
        }
    });
    
    // Ensure forms submit normally
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Remove any problematic hidden inputs
            const skipEmailInputs = this.querySelectorAll('input[name="_skip_auto_email"]');
            skipEmailInputs.forEach(input => input.remove());
            
            // Allow normal form submission
            return true;
        });
    });
    
    console.log('Admin navigation fix applied successfully');
});