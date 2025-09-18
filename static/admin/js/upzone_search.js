document.addEventListener('DOMContentLoaded', function() {
    const districtsSelect = document.querySelector('.mp-districts-select');
    if (!districtsSelect) return;

    // Create dual-pane interface
    const container = document.createElement('div');
    container.className = 'districts-container';
    
    // Available districts section
    const availableSection = document.createElement('div');
    availableSection.className = 'districts-section';
    availableSection.innerHTML = `
        <h4>उपलब्ध जिले</h4>
        <input type="text" class="district-search" placeholder="जिला खोजें..." id="search-available">
        <select multiple class="districts-list" id="available-districts" size="12"></select>
    `;
    
    // Selected districts section
    const selectedSection = document.createElement('div');
    selectedSection.className = 'districts-section';
    selectedSection.innerHTML = `
        <h4>चयनित जिले</h4>
        <input type="text" class="district-search" placeholder="जिला खोजें..." id="search-selected">
        <select multiple class="districts-list" id="selected-districts" size="12"></select>
    `;
    
    container.appendChild(availableSection);
    container.appendChild(selectedSection);
    
    // Replace original select with dual-pane
    districtsSelect.parentNode.insertBefore(container, districtsSelect);
    districtsSelect.style.display = 'none';
    
    const availableList = document.getElementById('available-districts');
    const selectedList = document.getElementById('selected-districts');
    
    // Populate available districts
    Array.from(districtsSelect.options).forEach(option => {
        const newOption = option.cloneNode(true);
        if (option.selected) {
            selectedList.appendChild(newOption);
        } else {
            availableList.appendChild(newOption);
        }
    });
    
    // Double-click to move districts
    availableList.addEventListener('dblclick', function(e) {
        if (e.target.tagName === 'OPTION') {
            selectedList.appendChild(e.target);
            updateOriginalSelect();
        }
    });
    
    selectedList.addEventListener('dblclick', function(e) {
        if (e.target.tagName === 'OPTION') {
            availableList.appendChild(e.target);
            updateOriginalSelect();
        }
    });
    
    // Update original select for form submission
    function updateOriginalSelect() {
        Array.from(districtsSelect.options).forEach(option => {
            option.selected = false;
        });
        Array.from(selectedList.options).forEach(option => {
            const originalOption = Array.from(districtsSelect.options).find(o => o.value === option.value);
            if (originalOption) originalOption.selected = true;
        });
    }
    
    // Search functionality
    function setupSearch(searchInput, targetList) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            Array.from(targetList.options).forEach(option => {
                const text = option.textContent.toLowerCase();
                option.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
    
    setupSearch(document.getElementById('search-available'), availableList);
    setupSearch(document.getElementById('search-selected'), selectedList);
});