// Multi-step registration form logic with conditional fields

document.addEventListener('DOMContentLoaded', () => {
    // Step navigation
    const steps = Array.from(document.querySelectorAll('.form-step'));
    const indicators = Array.from(document.querySelectorAll('.step-indicator .step'));
    const form = document.getElementById('registrationForm');
    let currentStep = 0;

    // Conditional field handlers
    function setupConditionalFields() {
        // Vehicle number field
        const transportSelect = document.querySelector('select[name="transport_mode"]');
        const vehicleRow = document.getElementById('vehicle-number-row');
        
        function toggleVehicleNumber() {
            if (transportSelect && transportSelect.value === 'car') {
                vehicleRow.style.display = 'block';
            } else {
                vehicleRow.style.display = 'none';
                // Clear vehicle number when not car
                const vehicleInput = document.querySelector('input[name="vehicle_number"]');
                if (vehicleInput) vehicleInput.value = '';
            }
        }
        
        if (transportSelect) {
            transportSelect.addEventListener('change', toggleVehicleNumber);
            // Initialize on page load
            toggleVehicleNumber();
        }

        // Volunteering details field
        const volunteerRadios = document.querySelectorAll('input[name="interested_in_volunteering"]');
        const volunteerRow = document.getElementById('volunteering-details-row');

        function toggleVolunteeringDetails() {
            const yesRadio = document.querySelector('input[name="interested_in_volunteering"][value="True"]');
            if (yesRadio && yesRadio.checked) {
                volunteerRow.style.display = 'block';
            } else {
                volunteerRow.style.display = 'none';
            }
        }

        volunteerRadios.forEach(radio => {
            radio.addEventListener('change', toggleVolunteeringDetails);
        });

        // On page load, set correct visibility
        toggleVolunteeringDetails();

        // Ensure youth_connect campaign is always checked
        const youthConnectCheckbox = document.querySelector('input[value="youth_connect"]');
        if (youthConnectCheckbox) {
            youthConnectCheckbox.checked = true;
            youthConnectCheckbox.addEventListener('change', (e) => {
                if (!e.target.checked) {
                    e.target.checked = true;
                    alert('युवा जोड़ो अभियान अनिवार्य है।');
                }
            });
        }
        
        // Special skills other field
        const skillsCheckboxes = document.querySelectorAll('input[name="special_skills"]');
        const otherSkillsRow = document.getElementById('other-skills-row');
        
        function toggleOtherSkillsField() {
            const otherCheckbox = document.querySelector('input[name="special_skills"][value="other"]');
            if (otherCheckbox && otherCheckbox.checked) {
                otherSkillsRow.style.display = 'block';
            } else {
                otherSkillsRow.style.display = 'none';
                // Clear the other field when hidden
                const otherInput = document.querySelector('input[name="special_skills_other"]');
                if (otherInput) otherInput.value = '';
            }
        }
        
        skillsCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', toggleOtherSkillsField);
        });
        
        // Initialize on page load
        toggleOtherSkillsField();
    }

    function showStep(index) {
        steps.forEach((step, i) => {
            step.classList.toggle('active', i === index);
            indicators[i].classList.toggle('active', i === index);
            indicators[i].classList.toggle('completed', i < index);
        });
        currentStep = index;
        if (index === 2) fillConfirmation();
    }

    window.nextStep = (stepNum) => {
        if (validateStep(stepNum - 1)) showStep(stepNum);
    };

    window.prevStep = (stepNum) => {
        showStep(stepNum - 2);
    };

    function validateStep(index) {
        const step = steps[index];
        let valid = true;
        
        // Special validation for step 1 - state and district required
        if (index === 0) {
            const stateField = step.querySelector('select[name="state"]');
            const districtField = step.querySelector('input[name="village_taluka"]');
            
            if (!stateField || !stateField.value.trim()) {
                if (stateField) stateField.classList.add('is-invalid');
                alert('कृपया राज्य का चयन करें।');
                valid = false;
            }
            
            if (!districtField || !districtField.value.trim()) {
                if (districtField) districtField.classList.add('is-invalid');
                alert('कृपया जिला/तालुका भरें।');
                valid = false;
            }
        }
        
        // Special validation for campaigns in step 2
        if (index === 1) {
            const checkedCampaigns = step.querySelectorAll('input[name="campaigns"]:checked');
            if (checkedCampaigns.length < 2) {
                alert('कृपया कम से कम दो अभियान चुनें।');
                valid = false;
            }
        }
        
        // Regular validation
        const inputs = step.querySelectorAll('input:not([type="radio"]):not([type="checkbox"]), select, textarea');
        inputs.forEach(input => {
            if (input.hasAttribute('required') && !input.value.trim()) {
                input.classList.add('is-invalid');
                valid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        // Validate radio buttons
        const radioGroups = {};
        step.querySelectorAll('input[type="radio"][required]').forEach(radio => {
            if (!radioGroups[radio.name]) {
                radioGroups[radio.name] = step.querySelectorAll(`input[name="${radio.name}"]`);
            }
        });
        
        Object.values(radioGroups).forEach(group => {
            const checked = Array.from(group).some(radio => radio.checked);
            if (!checked) {
                group.forEach(radio => radio.classList.add('is-invalid'));
                valid = false;
            } else {
                group.forEach(radio => radio.classList.remove('is-invalid'));
            }
        });
        
        return valid;
    }

    function fillConfirmation() {
        const summary = document.getElementById('confirmation-summary');
        if (!summary) return;
        
        const fields = [
            { label: 'नाम', name: 'full_name' },
            { label: 'मोबाइल', name: 'phone' },
            { label: 'ईमेल', name: 'email' },
            { label: 'जन्म तिथि', name: 'date_of_birth' },
            { label: 'लिंग', name: 'gender' },
            { label: 'शिक्षा', name: 'education' },
            { label: 'व्यवसाय', name: 'occupation' },
            { label: 'जिला', name: 'district' }
        ];
        
        let html = '<ul class="mb-0">';
        fields.forEach(field => {
            const input = form.querySelector(`[name="${field.name}"]`);
            if (input && input.value) {
                let value = input.value;
                if (input.tagName === 'SELECT') {
                    value = input.options[input.selectedIndex]?.text || '';
                }
                html += `<li><strong>${field.label}:</strong> ${value}</li>`;
            }
        });
        html += '</ul>';
        summary.innerHTML = html;
    }

    // Form submit validation
    form.addEventListener('submit', (e) => {
        const terms = document.getElementById('termsCheck');
        if (!terms.checked) {
            terms.classList.add('is-invalid');
            e.preventDefault();
            alert('कृपया नियम और शर्तों से सहमति दें।');
            return false;
        }
        
        // Validate all steps before submission
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
            alert('कृपया सभी आवश्यक फील्ड भरें।');
            return false;
        }
        
        terms.classList.remove('is-invalid');
        // Allow form submission
        return true;
    });

    // Real-time validation
    function setupRealTimeValidation() {
        // Phone validation
        const phoneInput = form.querySelector('input[name="phone"]');
        if (phoneInput) {
            phoneInput.addEventListener('input', function() {
                const value = this.value;
                const phonePattern = /^[0-9]{10}$/;
                
                if (value && !phonePattern.test(value)) {
                    this.classList.add('is-invalid');
                    showFieldError(this, 'कृपया 10 अंकों का मोबाइल नंबर दर्ज करें');
                } else {
                    this.classList.remove('is-invalid');
                    hideFieldError(this);
                }
            });
        }
        
        // Email validation
        const emailInput = form.querySelector('input[name="email"]');
        if (emailInput) {
            emailInput.addEventListener('input', function() {
                const value = this.value;
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                
                if (value && !emailPattern.test(value)) {
                    this.classList.add('is-invalid');
                    showFieldError(this, 'कृपया सही ईमेल पता दर्ज करें');
                } else {
                    this.classList.remove('is-invalid');
                    hideFieldError(this);
                }
            });
        }
        
        // Name validation
        const nameInput = form.querySelector('input[name="full_name"]');
        if (nameInput) {
            nameInput.addEventListener('input', function() {
                const value = this.value.trim();
                
                if (value && value.length < 2) {
                    this.classList.add('is-invalid');
                    showFieldError(this, 'नाम कम से कम 2 अक्षर का होना चाहिए');
                } else {
                    this.classList.remove('is-invalid');
                    hideFieldError(this);
                }
            });
        }
        
        // Date of birth validation
        const dobInput = form.querySelector('input[name="date_of_birth"]');
        if (dobInput) {
            dobInput.addEventListener('change', function() {
                const value = this.value;
                if (value) {
                    const birthDate = new Date(value);
                    const today = new Date();
                    const age = today.getFullYear() - birthDate.getFullYear();
                    
                    if (age < 16 || age > 100) {
                        this.classList.add('is-invalid');
                        showFieldError(this, 'आयु 16 से 100 वर्ष के बीच होनी चाहिए');
                    } else {
                        this.classList.remove('is-invalid');
                        hideFieldError(this);
                    }
                }
            });
        }
        
        // Required field validation
        form.querySelectorAll('input[required], select[required], textarea[required]').forEach(input => {
            input.addEventListener('blur', function() {
                if (!this.value.trim()) {
                    this.classList.add('is-invalid');
                    showFieldError(this, 'यह फील्ड आवश्यक है');
                } else {
                    this.classList.remove('is-invalid');
                    hideFieldError(this);
                }
            });
            
            input.addEventListener('input', function() {
                if (this.value.trim()) {
                    this.classList.remove('is-invalid');
                    hideFieldError(this);
                }
            });
        });
    }
    
    function showFieldError(field, message) {
        let errorDiv = field.parentNode.querySelector('.field-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'field-error text-danger small mt-1';
            field.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
    }
    
    function hideFieldError(field) {
        const errorDiv = field.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // Initialize
    setupConditionalFields();
    setupRealTimeValidation();
    showStep(0);
    
    // Backup submit handler
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            const terms = document.getElementById('termsCheck');
            if (!terms.checked) {
                e.preventDefault();
                alert('कृपया नियम और शर्तों से सहमति दें।');
                return false;
            }
            // If terms are checked, allow form submission
            form.submit();
        });
    }
});

// Registration type modal functions
function continueVolunteerRegistration() {
    const modal = document.getElementById('registrationTypeModal');
    const bootstrapModal = bootstrap.Modal.getInstance(modal);
    bootstrapModal.hide();
}

function goToRegularRegistration() {
    // Get current URL and replace volunteer-register with register
    const currentUrl = window.location.href;
    let regularUrl;
    
    if (currentUrl.includes('/volunteer-register/')) {
        regularUrl = currentUrl.replace('/volunteer-register/', '/register/');
    } else if (currentUrl.includes('/volunteer-register')) {
        regularUrl = currentUrl.replace('/volunteer-register', '/register');
    } else {
        // Fallback to events list
        regularUrl = '/events/';
    }
    
    window.location.href = regularUrl;
}

document.addEventListener('DOMContentLoaded', function() {
    // Show registration type modal on page load for volunteer registration
    const isVolunteerPage = window.location.href.includes('volunteer-register');
    if (isVolunteerPage) {
        const modal = new bootstrap.Modal(document.getElementById('registrationTypeModal'));
        modal.show();
    }
    
    function toggleVolunteeringDetails() {
        const yesRadio = document.querySelector('input[name="interested_in_volunteering"][value="True"]');
        const detailsGroup = document.getElementById('volunteering-details-group');
        if (yesRadio && yesRadio.checked) {
            detailsGroup.style.display = '';
        } else {
            detailsGroup.style.display = 'none';
        }
    }

    const radios = document.querySelectorAll('input[name="interested_in_volunteering"]');
    radios.forEach(radio => {
        radio.addEventListener('change', toggleVolunteeringDetails);
    });

    // On page load, set correct visibility
    toggleVolunteeringDetails();
});