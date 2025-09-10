console.log('Organization Registration JavaScript loaded!');

// Global variables
let steps, indicators, form, currentStep = 0;
let validationErrors = {};

// Real-time validation functions
function validateField(field) {
    const fieldName = field.name;
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Clear previous error
    clearFieldError(fieldName);

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'यह फील्ड आवश्यक है';
    }
    // Phone validation
    else if (fieldName === 'phone') {
        if (!/^\d{10}$/.test(value)) {
            isValid = false;
            errorMessage = 'मोबाइल नंबर 10 अंकों का होना चाहिए';
        }
    }
    // Email validation
    else if (fieldName === 'email') {
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            isValid = false;
            errorMessage = 'सही ईमेल पता दर्ज करें';
        }
    }
    // Date of birth validation
    else if (fieldName === 'date_of_birth') {
        if (value) {
            const birthDate = new Date(value);
            const today = new Date();
            const age = today.getFullYear() - birthDate.getFullYear();
            if (age < 16 || age > 80) {
                isValid = false;
                errorMessage = 'आयु 16 से 80 वर्ष के बीच होनी चाहिए';
            }
        }
    }
    // State and city validation
    else if ((fieldName === 'state' || fieldName === 'city') && field.tagName === 'SELECT') {
        if (!value || value === '') {
            isValid = false;
            errorMessage = fieldName === 'state' ? 'कृपया राज्य चुनें' : 'कृपया जिला/जनपद चुनें';
        }
    }
    // Responsibility validation
    else if (fieldName === 'responsibility') {
        if (!value || value === '') {
            isValid = false;
            errorMessage = 'कृपया जिम्मेदारी चुनें';
        }
    }

    // Update field styling and error display
    if (isValid) {
        field.classList.remove('error');
        field.classList.add('valid');
        validationErrors[fieldName] = false;
    } else {
        field.classList.remove('valid');
        field.classList.add('error');
        showFieldError(fieldName, errorMessage);
        validationErrors[fieldName] = true;
    }

    return isValid;
}

function showFieldError(fieldName, message) {
    const errorDiv = document.getElementById(`error-${fieldName}`);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
    }
}

function clearFieldError(fieldName) {
    const errorDiv = document.getElementById(`error-${fieldName}`);
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }
}

// Step validation
function validateStep(stepIndex) {
    const step = steps[stepIndex];
    if (!step) return false;

    const requiredFields = step.querySelectorAll('input[required], select[required]');
    let stepValid = true;
    let firstErrorField = null;

    requiredFields.forEach(field => {
        const isValid = validateField(field);
        if (!isValid && !firstErrorField) {
            firstErrorField = field;
        }
        stepValid = stepValid && isValid;
    });

    // Special validation for campaigns (only in step 2)
    if (stepIndex === 1) {
        const campaignCheckboxes = step.querySelectorAll('[name="campaigns"]:checked');
        if (campaignCheckboxes.length < 2) {
            showFieldError('campaigns', 'कृपया कम से कम 2 अभियान चुनें (युवा जोड़ो अभियान + एक और)');
            stepValid = false;
        } else {
            clearFieldError('campaigns');
        }

        // Check if youth_connect is selected
        const youthConnectSelected = Array.from(campaignCheckboxes).some(cb => cb.value === 'youth_connect');
        if (!youthConnectSelected) {
            showFieldError('campaigns', 'युवा जोड़ो अभियान अनिवार्य है');
            stepValid = false;
        }
    }

    // Focus on first error field
    if (!stepValid && firstErrorField) {
        firstErrorField.focus();
    }

    return stepValid;
}

// Navigation functions
function nextStep(currentStepIndex) {
    console.log('nextStep called with index:', currentStepIndex);
    
    if (!steps || steps.length === 0) {
        console.error('Steps not initialized');
        return;
    }
    
    // Validate current step
    if (!validateStep(currentStepIndex)) {
        return;
    }
    
    showStep(currentStepIndex + 1);
}

function prevStep(currentStepIndex) {
    showStep(currentStepIndex - 1);
}

function showStep(index) {
    if (!steps || !indicators) return;
    
    steps.forEach((step, i) => {
        step.classList.toggle('active', i === index);
        if (indicators[i]) {
            indicators[i].classList.toggle('active', i === index);
            indicators[i].classList.toggle('completed', i < index);
        }
    });
    
    currentStep = index;
    
    // Generate summary for step 3
    if (index === 2) {
        generateSummary();
    }
    
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function generateSummary() {
    const summaryDiv = document.getElementById('confirmation-summary');
    if (!summaryDiv || !form) return;
    
    const formData = new FormData(form);
    let html = '<div class="row">';
    
    // Personal Info
    html += '<div class="col-md-6"><h6>व्यक्तिगत जानकारी:</h6><ul>';
    html += `<li><strong>नाम:</strong> ${formData.get('full_name') || 'N/A'}</li>`;
    html += `<li><strong>फोन:</strong> ${formData.get('phone') || 'N/A'}</li>`;
    html += `<li><strong>ईमेल:</strong> ${formData.get('email') || 'N/A'}</li>`;
    html += `<li><strong>जिम्मेदारी:</strong> ${form.querySelector('[name="responsibility"] option:checked')?.textContent || 'N/A'}</li>`;
    html += '</ul></div>';
    
    // Other Info
    html += '<div class="col-md-6"><h6>अन्य जानकारी:</h6><ul>';
    html += `<li><strong>परिवहन:</strong> ${formData.get('transport_mode') || 'N/A'}</li>`;
    html += `<li><strong>शिक्षा:</strong> ${formData.get('education') || 'N/A'}</li>`;
    html += `<li><strong>व्यवसाय:</strong> ${formData.get('occupation') || 'N/A'}</li>`;
    html += `<li><strong>आगमन तिथि:</strong> ${formData.get('arrival_date') || 'N/A'}</li>`;
    html += '</ul></div>';
    
    html += '</div>';
    summaryDiv.innerHTML = html;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing organization registration...');
    
    steps = Array.from(document.querySelectorAll('.form-step'));
    indicators = Array.from(document.querySelectorAll('.step-indicator .step'));
    form = document.getElementById('registrationForm');
    
    console.log('Found steps:', steps.length);
    console.log('Found indicators:', indicators.length);
    
    if (steps.length === 0) {
        console.error('No form steps found!');
        return;
    }
    
    // Check if there are form errors and determine which step to show
    let initialStep = 0;
    if (form) {
        // Step 2 fields
        const step2Fields = ['transport_mode', 'arrival_date', 'vehicle_number', 'previous_shivir', 'interested_in_volunteering', 'volunteering_details', 'campaigns'];
        const step2HasError = step2Fields.some(name => {
            const el = form.querySelector(`[name="${name}"]`);
            return el && (el.classList.contains('is-invalid') || el.classList.contains('error'));
        });
        
        if (step2HasError) {
            initialStep = 1;
        } else {
            // Step 1 fields (including phone/email for duplicate errors)
            const step1Fields = ['full_name', 'phone', 'email', 'date_of_birth', 'gender', 'responsibility', 'education', 'occupation', 'village_taluka', 'state', 'city'];
            const step1HasError = step1Fields.some(name => {
                const el = form.querySelector(`[name="${name}"]`);
                return el && (el.classList.contains('is-invalid') || el.classList.contains('error'));
            });
            
            // For non-field errors (like duplicate phone/email), check error alert content
            const errorAlert = document.querySelector('.alert-danger');
            if (errorAlert && (errorAlert.textContent.includes('मोबाइल') || errorAlert.textContent.includes('ईमेल') || errorAlert.textContent.includes('phone') || errorAlert.textContent.includes('email'))) {
                initialStep = 0; // Show step 1 for phone/email related errors
            } else if (step1HasError) {
                initialStep = 0;
            }
        }
    }
    
    // Initialize appropriate step
    showStep(initialStep);
    console.log(`Initialized to step: ${initialStep}`);
    
    // Add real-time validation to all form fields
    const allFields = form.querySelectorAll('input, select');
    allFields.forEach(field => {
        // Validate on blur (when user leaves field)
        field.addEventListener('blur', () => {
            if (field.value.trim() || field.hasAttribute('required')) {
                validateField(field);
            }
        });
        
        // Validate on input for immediate feedback
        field.addEventListener('input', () => {
            if (field.classList.contains('error') || field.classList.contains('valid')) {
                validateField(field);
            }
        });
        
        // Special handling for phone number
        if (field.name === 'phone') {
            field.addEventListener('input', function(e) {
                const value = e.target.value.replace(/\D/g, '');
                if (value.length > 10) {
                    e.target.value = value.slice(0, 10);
                } else {
                    e.target.value = value;
                }
                validateField(field);
            });
        }
    });
    
    // Handle transport mode change
    const transportSelect = form.querySelector('[name="transport_mode"]');
    const vehicleRow = document.getElementById('vehicle-number-row');
    
    // Handle volunteering interest - show details field
    const volunteeringRadios = form.querySelectorAll('[name="interested_in_volunteering"]');
    const volunteeringDetailsRow = document.getElementById('volunteering-details-row');
    
    if (volunteeringRadios.length > 0 && volunteeringDetailsRow) {
        volunteeringRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'True' && this.checked) {
                    volunteeringDetailsRow.style.display = 'block';
                    const detailsInput = volunteeringDetailsRow.querySelector('[name="volunteering_details"]');
                    if (detailsInput) detailsInput.required = true;
                } else if (this.value === 'False' && this.checked) {
                    volunteeringDetailsRow.style.display = 'none';
                    const detailsInput = volunteeringDetailsRow.querySelector('[name="volunteering_details"]');
                    if (detailsInput) {
                        detailsInput.required = false;
                        detailsInput.value = '';
                    }
                }
            });
        });
    }
    
    if (transportSelect && vehicleRow) {
        transportSelect.addEventListener('change', function() {
            if (this.value === 'car') {
                vehicleRow.style.display = 'block';
                const vehicleInput = vehicleRow.querySelector('[name="vehicle_number"]');
                if (vehicleInput) vehicleInput.required = true;
            } else {
                vehicleRow.style.display = 'none';
                const vehicleInput = vehicleRow.querySelector('[name="vehicle_number"]');
                if (vehicleInput) {
                    vehicleInput.required = false;
                    vehicleInput.value = '';
                    clearFieldError('vehicle_number');
                }
            }
        });
    }
    
    // Handle form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submission started');
            
            const termsCheck = document.getElementById('termsCheck');
            if (!termsCheck || !termsCheck.checked) {
                e.preventDefault();
                alert('कृपया नियम और शर्तों से सहमति दें।');
                return false;
            }
            
            // Final validation of all steps
            let allValid = true;
            for (let i = 0; i < steps.length - 1; i++) {
                if (!validateStep(i)) {
                    allValid = false;
                    showStep(i);
                    break;
                }
            }
            
            if (!allValid) {
                e.preventDefault();
                alert('कृपया सभी त्रुटियों को ठीक करें।');
                return false;
            }
            
            console.log('Form validation passed, submitting...');
        });
    }
    
    console.log('Organization registration form initialized');
    console.log(`Current step after initialization: ${currentStep}`);
    
    // If there are errors, also log which fields have errors
    const errorFields = form.querySelectorAll('.is-invalid, .error');
    if (errorFields.length > 0) {
        console.log('Fields with errors:', Array.from(errorFields).map(f => f.name));
    }
});

// Make functions globally accessible
window.nextStep = nextStep;
window.prevStep = prevStep;
window.showStep = showStep;