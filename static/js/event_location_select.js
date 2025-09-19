document.addEventListener('DOMContentLoaded', function() {
    const countriesCSV = '/static/csv/countries.csv';
    const statesCSV = '/static/csv/states.csv';
    const citiesCSV = '/static/csv/cities.csv';
    let allCities = []; // Store all cities for faster filtering

    function parseCSV(text) {
        return text.trim().split('\n').map(row => row.split(','));
    }

    // Preload all cities on page load
    function preloadAllCities() {
        fetch(citiesCSV)
            .then(res => res.text())
            .then(text => {
                const rows = parseCSV(text);
                allCities = rows.slice(1); // Skip header
            })
            .catch(err => console.error('Failed to preload cities:', err));
    }

    function loadStates(countryName) {
        fetch(statesCSV)
            .then(res => res.text())
            .then(text => {
                const rows = parseCSV(text);
                const stateSelect = document.getElementById('id_state');
                stateSelect.innerHTML = '<option value="">राज्य चुनें</option>';
                rows.forEach((row, idx) => {
                    if (idx === 0) return; // skip header
                    if (row[4].replace(/"/g, '') === countryName) {
                        stateSelect.innerHTML += `<option value="${row[1].replace(/"/g, '')}">${row[1].replace(/"/g, '')}</option>`;
                    }
                });
            });
    }

    function loadCities(stateName) {
        const citySelect = document.getElementById('id_city');
        citySelect.innerHTML = '<option value="">जिला चुनें</option>';
        
        // Use preloaded cities for faster filtering
        allCities.forEach(row => {
            // row[4] is state_name in cities.csv
            if (row[4].replace(/"/g, '') === stateName) {
                citySelect.innerHTML += `<option value="${row[1].replace(/"/g, '')}">${row[1].replace(/"/g, '')}</option>`;
            }
        });
    }

    document.getElementById('id_country').addEventListener('change', function() {
        loadStates(this.value);
        document.getElementById('id_city').innerHTML = '<option value="">जिला चुनें</option>';
    });
    document.getElementById('id_state').addEventListener('change', function() {
        if (this.value) {
            loadCities(this.value);
        } else {
            document.getElementById('id_city').innerHTML = '<option value="">जिला चुनें</option>';
        }
    });

    // Preload cities and set default country
    preloadAllCities();
    loadStates('India');
});