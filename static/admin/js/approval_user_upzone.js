document.addEventListener('DOMContentLoaded', function() {
    const stateApprover = document.getElementById('id_is_state_approver');
    const upzoneApprover = document.getElementById('id_is_upzone_approver');
    const districtApprover = document.getElementById('id_is_district_approver');
    const upzoneField = document.querySelector('.field-upzone');
    const districtsField = document.querySelector('.field-districts');
    
    function toggleFields() {
        // Hide all assignment fields first
        if (upzoneField) upzoneField.style.display = 'none';
        if (districtsField) districtsField.style.display = 'none';
        
        // Show relevant fields based on selection
        if (upzoneApprover && upzoneApprover.checked) {
            if (upzoneField) upzoneField.style.display = 'block';
        }
        
        if (districtApprover && districtApprover.checked) {
            if (districtsField) districtsField.style.display = 'block';
        }
        
        // Ensure only one approver type is selected
        if (stateApprover && stateApprover.checked) {
            if (upzoneApprover) upzoneApprover.checked = false;
            if (districtApprover) districtApprover.checked = false;
        }
        
        if (upzoneApprover && upzoneApprover.checked) {
            if (stateApprover) stateApprover.checked = false;
            if (districtApprover) districtApprover.checked = false;
        }
        
        if (districtApprover && districtApprover.checked) {
            if (stateApprover) stateApprover.checked = false;
            if (upzoneApprover) upzoneApprover.checked = false;
        }
    }
    
    // Add event listeners
    if (stateApprover) stateApprover.addEventListener('change', toggleFields);
    if (upzoneApprover) upzoneApprover.addEventListener('change', toggleFields);
    if (districtApprover) districtApprover.addEventListener('change', toggleFields);
    
    // Initial toggle
    toggleFields();
});