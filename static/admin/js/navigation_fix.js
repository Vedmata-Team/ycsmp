// Navigation Fix for Admin Panel
// This script ensures normal admin navigation works properly

document.addEventListener('DOMContentLoaded', function() {
    console.log('Navigation fix loaded');
    
    // Prevent any script from interfering with normal admin navigation
    const adminLinks = document.querySelectorAll('a[href*="/admin/"], a[href*="/control/"]');
    
    adminLinks.forEach(link => {
        // Remove any existing click event listeners that might interfere
        const newLink = link.cloneNode(true);
        link.parentNode.replaceChild(newLink, link);
        
        // Ensure normal navigation behavior
        newLink.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Allow normal navigation for admin links
            if (href && (href.includes('/admin/') || href.includes('/control/'))) {
                // Don't prevent default - let browser handle normally
                console.log('Allowing normal navigation to:', href);
                return true;
            }
        });
    });
    
    // Fix for breadcrumb navigation
    const breadcrumbs = document.querySelectorAll('.breadcrumbs a');
    breadcrumbs.forEach(link => {
        link.addEventListener('click', function(e) {
            // Ensure breadcrumb navigation works normally
            const href = this.getAttribute('href');
            if (href) {
                window.location.href = href;
            }
        });
    });
    
    // Fix for model links in admin index
    const modelLinks = document.querySelectorAll('.model-link, .addlink, .changelink');
    modelLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && !href.startsWith('#')) {
                // Ensure model navigation works
                window.location.href = href;
            }
        });
    });
});