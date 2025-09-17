document.addEventListener('DOMContentLoaded', function() {
    const countriesCSV = '/static/csv/countries.csv';
    const statesCSV = '/static/csv/states.csv';
    const citiesCSV = '/static/csv/cities.csv';

    function parseCSV(text) {
        return text.trim().split('\n').map(row => row.split(','));
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
                // Optionally trigger city load for first state
                // loadCities(stateSelect.value);
            });
    }

    function loadCities(stateName) {
        const citySelect = document.getElementById('id_city');
        citySelect.innerHTML = '<option value="">लोड हो रहा है...</option>';
        citySelect.disabled = true;
        
        fetch(citiesCSV)
            .then(res => res.text())
            .then(text => {
                const rows = parseCSV(text);
                citySelect.innerHTML = '<option value="">जनपद/जिला चुनें</option>';
                rows.forEach((row, idx) => {
                    if (idx === 0) return; // skip header
                    // row[4] is state_name in cities.csv
                    if (row[4].replace(/"/g, '') === stateName) {
                        citySelect.innerHTML += `<option value="${row[1].replace(/"/g, '')}">${row[1].replace(/"/g, '')}</option>`;
                    }
                });
                citySelect.disabled = false;
            })
            .catch(() => {
                citySelect.innerHTML = '<option value="">त्रुटि - पुनः प्रयास करें</option>';
                citySelect.disabled = false;
            });
    }

    document.getElementById('id_country').addEventListener('change', function() {
        loadStates(this.value);
        document.getElementById('id_city').innerHTML = '<option value="">जनपद/जिला चुनें</option>';
    });
    document.getElementById('id_state').addEventListener('change', function() {
        if (this.value) {
            loadCities(this.value);
        } else {
            document.getElementById('id_city').innerHTML = '<option value="">जनपद/जिला चुनें</option>';
        }
    });

    // On pages load, set default country and load states
    loadStates('India');
});