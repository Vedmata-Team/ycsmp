// Admin Filter Persistence System
// Maintains filter state across page reloads and actions

document.addEventListener('DOMContentLoaded', function() {
    const STORAGE_KEY = 'admin_filters_' + window.location.pathname;
    
    // Initialize filter persistence
    initFilterPersistence();
    
    // Handle edit page redirects
    handleEditPageRedirects();
    
    function initFilterPersistence() {
        // Restore filters on page load
        restoreFilters();
        
        // Save filters when they change
        attachFilterListeners();
        
        // Handle form submissions to preserve filters
        handleFormSubmissions();
        
        // Handle pagination and sorting links
        handleNavigationLinks();
    }
    
    function restoreFilters() {
        const savedFilters = getSavedFilters();
        if (!savedFilters || Object.keys(savedFilters).length === 0) {
            return;
        }
        
        // Check if current URL already has filters
        const currentParams = new URLSearchParams(window.location.search);
        let hasFilters = false;
        
        // Check if any filter parameters exist in current URL
        for (const key in savedFilters) {
            if (currentParams.has(key)) {
                hasFilters = true;
                break;
            }
        }
        
        // Only restore if no filters are currently applied
        if (!hasFilters) {
            const newUrl = buildUrlWithFilters(savedFilters);
            if (newUrl !== window.location.href) {
                window.location.href = newUrl;
                return;
            }
        }
        
        // Update saved filters with current state
        saveCurrentFilters();
    }
    
    function attachFilterListeners() {
        // Listen to filter sidebar links
        const filterSidebar = document.getElementById('changelist-filter');
        if (filterSidebar) {
            filterSidebar.addEventListener('click', function(e) {
                if (e.target.tagName === 'A') {
                    setTimeout(saveCurrentFilters, 100);
                }
            });
        }
        
        // Listen to search form
        const searchForm = document.getElementById('changelist-search');
        if (searchForm) {
            const searchInput = searchForm.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.addEventListener('input', debounce(saveCurrentFilters, 500));
            }
        }
        
        // Listen to date hierarchy
        const dateHierarchy = document.querySelector('.date-hierarchy');
        if (dateHierarchy) {
            dateHierarchy.addEventListener('click', function(e) {
                if (e.target.tagName === 'A') {
                    setTimeout(saveCurrentFilters, 100);
                }
            });
        }
    }
    
    function handleFormSubmissions() {
        // Handle action form submissions
        const actionForm = document.getElementById('changelist-form');
        if (actionForm) {
            actionForm.addEventListener('submit', function(e) {
                const formData = new FormData(actionForm);
                const action = formData.get('action');
                
                if (action && action !== '---------') {
                    // Save current filters before action
                    saveCurrentFilters();
                    
                    // Add filter parameters to form
                    const savedFilters = getSavedFilters();
                    for (const key in savedFilters) {
                        if (!formData.has(key)) {
                            const input = document.createElement('input');
                            input.type = 'hidden';
                            input.name = key;
                            input.value = savedFilters[key];
                            actionForm.appendChild(input);
                        }
                    }
                }
            });
        }
        
        // Handle individual edit form submissions
        const editForms = document.querySelectorAll('form');
        editForms.forEach(form => {
            if (form.id !== 'changelist-form' && form.method.toLowerCase() === 'post') {
                form.addEventListener('submit', function(e) {
                    // Save current filters before form submission
                    saveCurrentFilters();
                });
            }
        });
    }
    
    function handleNavigationLinks() {
        // Handle pagination links
        const paginationLinks = document.querySelectorAll('.paginator a');
        paginationLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const href = this.getAttribute('href');
                const newUrl = addFiltersToUrl(href, getSavedFilters());
                window.location.href = newUrl;
            });
        });
        
        // Handle column sorting links
        const sortingLinks = document.querySelectorAll('#result_list th a');
        sortingLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const href = this.getAttribute('href');
                const newUrl = addFiltersToUrl(href, getSavedFilters());
                window.location.href = newUrl;
            });
        });
    }
    
    function saveCurrentFilters() {
        const currentParams = new URLSearchParams(window.location.search);
        const filters = {};
        
        // Extract filter parameters (exclude system parameters)
        const systemParams = ['p', 'o', '_changelist_filters', '_popup', '_to_field'];
        
        for (const [key, value] of currentParams.entries()) {
            if (!systemParams.includes(key) && value) {
                filters[key] = value;
            }
        }
        
        // Save to localStorage
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
        } catch (e) {
            console.warn('Could not save filters to localStorage:', e);
        }
    }
    
    function getSavedFilters() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            console.warn('Could not load filters from localStorage:', e);
            return {};
        }
    }
    
    function buildUrlWithFilters(filters) {
        const baseUrl = window.location.pathname;
        const params = new URLSearchParams(window.location.search);
        
        // Add saved filters
        for (const key in filters) {
            params.set(key, filters[key]);
        }
        
        return baseUrl + '?' + params.toString();
    }
    
    function addFiltersToUrl(url, filters) {
        const urlObj = new URL(url, window.location.origin);
        
        // Add saved filters to the URL
        for (const key in filters) {
            if (!urlObj.searchParams.has(key)) {
                urlObj.searchParams.set(key, filters[key]);
            }
        }
        
        return urlObj.toString();
    }
    
    // Handle edit page redirects
    function handleEditPageRedirects() {
        // Check if we're on an edit page and need to redirect back with filters
        if (window.location.pathname.includes('/change/')) {
            const savedFilters = getSavedFilters();
            if (Object.keys(savedFilters).length > 0) {
                // Add hidden inputs to preserve filters on save
                const forms = document.querySelectorAll('form[method="post"]');
                forms.forEach(form => {
                    for (const key in savedFilters) {
                        const existingInput = form.querySelector(`input[name="${key}"]`);
                        if (!existingInput) {
                            const input = document.createElement('input');
                            input.type = 'hidden';
                            input.name = key;
                            input.value = savedFilters[key];
                            form.appendChild(input);
                        }
                    }
                });
            }
        }
    }
    
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Add clear filters functionality
    addClearFiltersButton();
    
    function addClearFiltersButton() {
        const filterSidebar = document.getElementById('changelist-filter');
        if (filterSidebar && Object.keys(getSavedFilters()).length > 0) {
            const clearButton = document.createElement('div');
            clearButton.innerHTML = `
                <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;">
                    <button type="button" id="clear-filters-btn" style="
                        background: #dc3545; 
                        color: white; 
                        border: none; 
                        padding: 8px 16px; 
                        border-radius: 4px; 
                        cursor: pointer;
                        font-size: 12px;
                        width: 100%;
                    ">
                        🗑️ Clear All Filters
                    </button>
                </div>
            `;
            
            filterSidebar.insertBefore(clearButton, filterSidebar.firstChild);
            
            document.getElementById('clear-filters-btn').addEventListener('click', function() {
                // Clear saved filters
                localStorage.removeItem(STORAGE_KEY);
                
                // Redirect to clean URL
                window.location.href = window.location.pathname;
            });
        }
    }
    
    // Show filter status indicator
    showFilterStatus();
    
    function showFilterStatus() {
        const savedFilters = getSavedFilters();
        const filterCount = Object.keys(savedFilters).length;
        
        if (filterCount > 0) {
            const statusIndicator = document.createElement('div');
            statusIndicator.innerHTML = `
                <div style="
                    position: fixed; 
                    top: 32px; 
                    right: 20px; 
                    background: #28a745; 
                    color: white; 
                    padding: 8px 12px; 
                    border-radius: 4px; 
                    font-size: 12px; 
                    z-index: 1000;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                ">
                    📌 ${filterCount} filter(s) active
                </div>
            `;
            document.body.appendChild(statusIndicator);
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                statusIndicator.remove();
            }, 3000);
        }
    }
});