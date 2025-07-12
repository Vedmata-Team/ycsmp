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

    // Remove invalid class on input
    form.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('input', () => input.classList.remove('is-invalid'));
    });

    // Initialize
    setupConditionalFields();
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

document.addEventListener('DOMContentLoaded', function() {
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