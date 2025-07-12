document.addEventListener('DOMContentLoaded', function() {
    const stateCodeField = document.getElementById('id_state_code');
    const districtsField = document.querySelector('.field-districts');
    const isDistrictApproverField = document.getElementById('id_is_district_approver');
    const isStateApproverField = document.getElementById('id_is_state_approver');
    
    function setupSearchableDistricts() {
        const districtsWidget = document.querySelector('.searchable-districts');
        if (!districtsWidget) return;
        
        // Create search input
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'districts-search';
        searchInput.placeholder = 'जिले खोजें...';
        
        // Create select all checkbox
        const selectAllLabel = document.createElement('label');
        selectAllLabel.className = 'select-all-districts';
        const selectAllCheckbox = document.createElement('input');
        selectAllCheckbox.type = 'checkbox';
        selectAllLabel.appendChild(selectAllCheckbox);
        selectAllLabel.appendChild(document.createTextNode(' सभी चुनें'));
        
        // Wrap existing checkboxes in container
        const container = document.createElement('div');
        container.className = 'districts-container';
        const checkboxes = districtsWidget.querySelectorAll('label');
        checkboxes.forEach(label => container.appendChild(label));
        
        // Insert elements
        districtsWidget.insertBefore(searchInput, districtsWidget.firstChild);
        districtsWidget.insertBefore(selectAllLabel, districtsWidget.firstChild.nextSibling);
        districtsWidget.appendChild(container);
        
        // Search functionality
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            checkboxes.forEach(function(label) {
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
            checkboxes.forEach(function(label) {
                if (!label.classList.contains('hidden')) {
                    const checkbox = label.querySelector('input[type="checkbox"]');
                    if (checkbox) checkbox.checked = isChecked;
                }
            });
        });
    }
    
    function toggleDistrictsField() {
        if (stateCodeField && districtsField) {
            if (stateCodeField.value === 'MP') {
                districtsField.style.display = 'block';
                setupSearchableDistricts();
            } else {
                districtsField.style.display = 'none';
                const checkboxes = districtsField.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(cb => cb.checked = false);
            }
        }
    }
    
    function toggleApproverFields() {
        if (stateCodeField && isDistrictApproverField && isStateApproverField) {
            if (stateCodeField.value === 'MP') {
                isDistrictApproverField.disabled = false;
                isStateApproverField.checked = false;
                isStateApproverField.disabled = true;
            } else {
                isStateApproverField.disabled = false;
                isDistrictApproverField.checked = false;
                isDistrictApproverField.disabled = true;
            }
        }
    }
    
    if (stateCodeField) {
        stateCodeField.addEventListener('change', function() {
            toggleDistrictsField();
            toggleApproverFields();
        });
        
        toggleDistrictsField();
        toggleApproverFields();
    }
});