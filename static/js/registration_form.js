console.log('JavaScript file loaded!');

// Global variables
let steps, indicators, form, currentStep = 0;

// Global functions accessible to HTML onclick handlers
function nextStep(currentStepIndex) {
    console.log('nextStep called with index:', currentStepIndex);
    
    if (!steps || steps.length === 0) {
        console.error('Steps not initialized');
        return;
    }
    
    const step = steps[currentStepIndex];
    if (!step) {
        console.error('Step not found:', currentStepIndex);
        return;
    }
    
    // Simple validation - check required fields and patterns
    const requiredInputs = step.querySelectorAll('input[required], select[required]');
    let valid = true;
    
    requiredInputs.forEach(input => {
        let isValid = true;
        
        // Check if field is empty
        if (!input.value.trim()) {
            isValid = false;
        }
        // Special validation for phone
        else if (input.name === 'phone' && input.value.length !== 10) {
            isValid = false;
        }
        // Special validation for state and city dropdowns
        else if ((input.name === 'state' || input.name === 'city') && (!input.value || input.value === '')) {
            isValid = false;
        }
        
        if (isValid) {
            input.classList.remove('is-invalid');
        } else {
            input.classList.add('is-invalid');
            valid = false;
        }
    });
    
    // Additional check for state and city selection
    const stateSelect = step.querySelector('[name="state"]');
    const citySelect = step.querySelector('[name="city"]');
    
    if (stateSelect && (!stateSelect.value || stateSelect.value === '')) {
        stateSelect.classList.add('is-invalid');
        valid = false;
    }
    
    if (citySelect && (!citySelect.value || citySelect.value === '')) {
        citySelect.classList.add('is-invalid');
        valid = false;
    }
    
    if (valid) {
        showStep(currentStepIndex + 1);
    } else {
        // Check specifically for state/city issues
        const stateSelect = step.querySelector('[name="state"]');
        const citySelect = step.querySelector('[name="city"]');
        
        if (stateSelect && (!stateSelect.value || stateSelect.value === '')) {
            alert('कृपया राज्य चुनें।');
        } else if (citySelect && (!citySelect.value || citySelect.value === '')) {
            alert('कृपया जिला/जनपद चुनें।');
        } else {
            alert('कृपया सभी आवश्यक फील्ड भरें।');
        }
    }
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
    html += `<li><strong>जन्म तिथि:</strong> ${formData.get('date_of_birth') || 'N/A'}</li>`;
    html += `<li><strong>लिंग:</strong> ${formData.get('gender') || 'N/A'}</li>`;
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
    console.log('DOM loaded, initializing...');
    
    // Check if this is after a form submission
    if (window.formSubmitted) {
        console.log('Page reloaded after form submission - this indicates an error');
    } else {
        console.log('Fresh page load');
    }
    
    steps = Array.from(document.querySelectorAll('.form-step'));
    indicators = Array.from(document.querySelectorAll('.step-indicator .step'));
    form = document.getElementById('registrationForm');
    
    console.log('Found steps:', steps.length);
    console.log('Found indicators:', indicators.length);
    
    if (steps.length === 0) {
        console.error('No form steps found!');
        return;
    }
    
    // Initialize first step
    showStep(0);
    
    // Add phone validation
    const phoneInput = form.querySelector('[name="phone"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            const value = e.target.value;
            if (value.length > 10) {
                e.target.value = value.slice(0, 10);
                alert('मोबाइल नंबर 10 अंक से ज्यादा नहीं हो सकता।');
            }
        });
    }
    
    // Remove date restrictions
    const dobInput = form.querySelector('[name="date_of_birth"]');
    if (dobInput) {
        dobInput.removeAttribute('min');
        dobInput.removeAttribute('max');
    }
    
    // Handle transport mode change - show vehicle number for car
    const transportSelect = form.querySelector('[name="transport_mode"]');
    const vehicleRow = document.getElementById('vehicle-number-row');
    
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
                }
            }
        });
        
        // Trigger change event on page load
        transportSelect.dispatchEvent(new Event('change'));
    }
    
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
    
    // Handle special skills other field
    const specialSkillsCheckboxes = form.querySelectorAll('[name="special_skills"]');
    const otherSkillsRow = document.getElementById('other-skills-row');
    
    if (specialSkillsCheckboxes.length > 0 && otherSkillsRow) {
        specialSkillsCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const otherChecked = Array.from(specialSkillsCheckboxes).some(cb => cb.value === 'other' && cb.checked);
                if (otherChecked) {
                    otherSkillsRow.style.display = 'block';
                } else {
                    otherSkillsRow.style.display = 'none';
                    const otherInput = otherSkillsRow.querySelector('[name="special_skills_other"]');
                    if (otherInput) otherInput.value = '';
                }
            });
        });
    }
    
    // Handle form submission with debugging
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('=== FORM SUBMISSION DEBUG ===');
            console.log('Form submit event triggered');
            console.log('Current step:', currentStep);
            console.log('Form action:', form.action);
            console.log('Form method:', form.method);
            
            const termsCheck = document.getElementById('termsCheck');
            console.log('Terms checkbox found:', !!termsCheck);
            console.log('Terms checked:', termsCheck ? termsCheck.checked : 'N/A');
            
            if (!termsCheck || !termsCheck.checked) {
                console.log('PREVENTING SUBMIT: Terms not checked');
                e.preventDefault();
                alert('कृपया नियम और शर्तों से सहमति दें।');
                return false;
            }
            
            // Check if we're on the final step
            if (currentStep !== 2) {
                console.log('PREVENTING SUBMIT: Not on final step, current step:', currentStep);
                e.preventDefault();
                alert('कृपया पहले सभी स्टेप पूरे करें।');
                return false;
            }
            
            // Validate all required fields
            const allRequiredInputs = form.querySelectorAll('input[required], select[required]');
            let hasErrors = false;
            
            console.log('Validating', allRequiredInputs.length, 'required fields');
            
            allRequiredInputs.forEach((input, index) => {
                const isEmpty = !input.value.trim();
                const isPhoneInvalid = input.name === 'phone' && input.value.length !== 10;
                
                if (isEmpty || isPhoneInvalid) {
                    console.log(`Field ${index + 1} (${input.name}) validation failed:`, {
                        value: input.value,
                        isEmpty,
                        isPhoneInvalid
                    });
                    hasErrors = true;
                }
            });
            
            if (hasErrors) {
                console.log('PREVENTING SUBMIT: Validation errors found');
                e.preventDefault();
                alert('कृपया सभी आवश्यक फील्ड भरें।');
                return false;
            }
            
            console.log('ALLOWING SUBMIT: All validations passed');
            console.log('Form will be submitted normally');
            
            // Log form data being submitted
            const formData = new FormData(form);
            console.log('Form data being submitted:');
            for (let [key, value] of formData.entries()) {
                console.log(`  ${key}: ${value}`);
            }
            
            // Add a flag to track submission
            window.formSubmitted = true;
            console.log('Form submission flag set');
        });
    }
    
    console.log('Registration form initialized');
    console.log('Form element:', form);
    console.log('Form action:', form ? form.action : 'No form');
    console.log('Form method:', form ? form.method : 'No form');
});

// Form filler function for testing
function fillTestData() {
    if (!form) return;
    
    // Fill Step 1
    const fullName = form.querySelector('[name="full_name"]');
    if (fullName) fullName.value = 'Test User';
    
    const phone = form.querySelector('[name="phone"]');
    if (phone) phone.value = '9876543210';
    
    const email = form.querySelector('[name="email"]');
    if (email) email.value = 'test@example.com';
    
    const dob = form.querySelector('[name="date_of_birth"]');
    if (dob) dob.value = '1990-01-01';
    
    const gender = form.querySelector('[name="gender"]');
    if (gender) gender.value = 'M';
    
    const transport = form.querySelector('[name="transport_mode"]');
    if (transport) {
        transport.value = 'car';
        transport.dispatchEvent(new Event('change'));
    }
    
    setTimeout(() => {
        const vehicle = form.querySelector('[name="vehicle_number"]');
        if (vehicle) vehicle.value = 'MP01AB1234';
    }, 100);
    
    const education = form.querySelector('[name="education"]');
    if (education) education.value = 'graduation';
    
    const occupation = form.querySelector('[name="occupation"]');
    if (occupation) occupation.value = 'Engineer';
    
    const previousShivir = form.querySelector('[name="previous_shivir"][value="True"]');
    if (previousShivir) previousShivir.checked = true;
    
    const village = form.querySelector('[name="village_taluka"]');
    if (village) village.value = 'Test Village';
    
    const state = form.querySelector('[name="state"]');
    if (state) state.value = 'MP';
    
    setTimeout(() => {
        const city = form.querySelector('[name="city"]');
        if (city) city.value = 'Bhopal';
    }, 200);
    
    // Fill Step 2
    const arrivalDate = form.querySelector('[name="arrival_date"]');
    if (arrivalDate) arrivalDate.value = '2025-10-26';
    
    const volunteering = form.querySelector('[name="interested_in_volunteering"][value="True"]');
    if (volunteering) volunteering.checked = true;
    
    const campaigns = form.querySelectorAll('[name="campaigns"]');
    if (campaigns.length > 0) {
        campaigns[0].checked = true; // Check first campaign
        if (campaigns.length > 1) campaigns[1].checked = true; // Check second campaign
    }
    
    console.log('Test data filled!');
}

// Make functions globally accessible
window.nextStep = nextStep;
window.prevStep = prevStep;
window.showStep = showStep;
window.generateSummary = generateSummary;
window.fillTestData = fillTestData;