document.addEventListener('DOMContentLoaded', function() {
    let statesData = [];
    let citiesData = [];

    // Load all data once when page loads
    Promise.all([
        fetch('/api/states/').then(res => res.json()),
        fetch('/api/cities/').then(res => res.json())
    ]).then(([statesResponse, citiesResponse]) => {
        statesData = statesResponse.states;
        citiesData = citiesResponse.cities;
        populateStates();
    }).catch(err => console.error('Failed to load location data:', err));

    function populateStates() {
        const stateSelect = document.getElementById('id_state');
        stateSelect.innerHTML = '<option value="">राज्य चुनें</option>';
        statesData.forEach(state => {
            stateSelect.innerHTML += `<option value="${state.name}" data-id="${state.id}">${state.name}</option>`;
        });
    }

    function loadCities(stateId) {
        const citySelect = document.getElementById('id_city');
        citySelect.innerHTML = '<option value="">जिला चुनें</option>';
        
        if (!stateId) return;
        
        // Filter cities instantly from local data
        const stateCities = citiesData.filter(city => city.state_id == stateId);
        stateCities.forEach(city => {
            citySelect.innerHTML += `<option value="${city.name}">${city.name}</option>`;
        });
    }

    document.getElementById('id_country').addEventListener('change', function() {
        if (this.value === 'India') {
            populateStates();
        }
        document.getElementById('id_city').innerHTML = '<option value="">जिला चुनें</option>';
    });
    
    document.getElementById('id_state').addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const stateId = selectedOption.getAttribute('data-id');
        if (stateId) {
            loadCities(stateId);
        } else {
            document.getElementById('id_city').innerHTML = '<option value="">जिला चुनें</option>';
        }
    });
});