let selectedFieldValues = []; 
let csv_file_categorical_field_list_front = [];

document.getElementById("colormap_file_input").addEventListener("change", function (event) {
    const file = event.target.files[0];

    if (file && file.name.toLowerCase().endsWith('.csv')) {
        const reader = new FileReader();

        reader.onload = function () {
            const csvContent = reader.result;
            
            processCSV(csvContent);
            console.log("CSV File: ", csvContent)
            document.getElementById('file_data').value = csvContent;
        };
        reader.readAsText(file);
    } else {
        alert('Please select a CSV file.');
        event.target.value = '';
    }
});

function processCSV(csvContent) {
    const rows = csvContent.split("\n").map(row => row.split(","));
    if (rows.length < 2) return;
    const headers = rows[0];
    const data = rows.slice(1);
    populateDropdown(headers, data);
}

function populateDropdown(headers, data) {
    const dropdown = document.getElementById("search_field");
    dropdown.innerHTML = '<option value="" disabled selected>Select a field</option>';
    headers.forEach((header, index) => {
        const option = document.createElement("option");
        option.value = index;
        option.textContent = header.trim();
        dropdown.appendChild(option);
    });
    dropdown.addEventListener("change", function () {
        const selectedIndex = this.value;
        selectedFieldValues = getFieldData(selectedIndex, data);
        console.log('Selected Field Values:', selectedFieldValues);
    });
}

function getFieldData(fieldIndex, data) {
    const values = data.map(row => {
        let cell = row[fieldIndex];
        if (cell) {
            cell = cell.replace(/"/g, "");
            cell = cell.trim();
        } else {
            cell = "";
        }
        return cell;
    });
    const uniqueValues = [...new Set(values.filter(value => value !== ""))];
    return uniqueValues;
}

document.getElementById('add_pair_button').addEventListener('click', function() {
    const searchFieldDropdown = document.getElementById('search_field');
    const searchField = searchFieldDropdown.options[searchFieldDropdown.selectedIndex].text.trim();
    const formattedField = [searchField + '|'];
    csv_file_categorical_field_list_front.push(formattedField);
    updateDisplay();
});

function updateDisplay() {
    const savedPairsContainer = document.getElementById('saved_pairs_container');
    savedPairsContainer.innerHTML = '';
    csv_file_categorical_field_list_front.forEach(pair => {
        const div = document.createElement('div');
        div.textContent = pair[0];
        savedPairsContainer.appendChild(div);
    });
}

document.querySelector('form').addEventListener('submit', function(event) {
    const fileInput = document.getElementById('colormap_file_input');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a CSV file before submitting the form.');
        event.preventDefault();
        return;
    } else if (!file.name.toLowerCase().endsWith('.csv')) {
        alert('The selected file must be a CSV.');
        event.preventDefault();
        return;
    }
    
    console.log('Form data to be submitted:', JSON.stringify(csv_file_categorical_field_list_front));
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'csv_file_categorical_field_list_front';
    console.log(csv_file_categorical_field_list_front); 
    hiddenInput.value = JSON.stringify(csv_file_categorical_field_list_front);
    console.log(JSON.stringify(csv_file_categorical_field_list_front)); 
    this.appendChild(hiddenInput);
});