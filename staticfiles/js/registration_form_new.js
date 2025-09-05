console.log('New JavaScript file loaded!');

let steps, indicators, form, currentStep = 0;

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
    
    // Simple validation - check required fields
    const requiredInputs = step.querySelectorAll('input[required], select[required]');
    let valid = true;
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            valid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    if (valid) {
        showStep(currentStepIndex + 1);
    } else {
        alert('कृपया सभी आवश्यक फील्ड भरें।');
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
    
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing...');
    
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
    
    console.log('Registration form initialized');
});