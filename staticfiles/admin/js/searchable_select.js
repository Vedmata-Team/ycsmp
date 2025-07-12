document.addEventListener('DOMContentLoaded', function() {
    const containers = document.querySelectorAll('.searchable-select-container');
    
    containers.forEach(function(container) {
        const searchInput = container.querySelector('.searchable-input');
        const selectAllCheckbox = container.querySelector('.select-all-checkbox');
        const optionLabels = container.querySelectorAll('.option-label');
        const checkboxes = container.querySelectorAll('.option-label input[type="checkbox"]');
        
        // Search functionality
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            optionLabels.forEach(function(label) {
                const text = label.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    label.classList.remove('hidden');
                } else {
                    label.classList.add('hidden');
                }
            });
        });
        
        // Select all functionality
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            
            checkboxes.forEach(function(checkbox) {
                const label = checkbox.closest('.option-label');
                if (!label.classList.contains('hidden')) {
                    checkbox.checked = isChecked;
                }
            });
        });
        
        // Update select all checkbox when individual checkboxes change
        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                const visibleCheckboxes = Array.from(checkboxes).filter(cb => 
                    !cb.closest('.option-label').classList.contains('hidden')
                );
                const checkedVisibleCheckboxes = visibleCheckboxes.filter(cb => cb.checked);
                
                selectAllCheckbox.checked = visibleCheckboxes.length > 0 && 
                    checkedVisibleCheckboxes.length === visibleCheckboxes.length;
                selectAllCheckbox.indeterminate = checkedVisibleCheckboxes.length > 0 && 
                    checkedVisibleCheckboxes.length < visibleCheckboxes.length;
            });
        });
    });
});