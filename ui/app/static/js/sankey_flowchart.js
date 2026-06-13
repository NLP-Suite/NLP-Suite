let savedFields = "";

    document.getElementById("sankey_file_input").addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file && file.name.toLowerCase().endsWith('.csv')) {
            const reader = new FileReader();
            reader.onload = function () {
                const csvContent = reader.result;
                console.log("CSV File: ", csvContent);
                
                const csvArray = csvContent.trim().split("\n").map(row => row.split(",").map(cell => cell.trim()));
                if (csvArray.length < 2) {
                    alert("CSV file must have at least one row of data.");
                    return;
                }

                const headers = csvArray[0];
                const data = csvArray.slice(1).map(row => {
                    let obj = {};
                    headers.forEach((header, index) => {
                        obj[header] = row[index] ? row[index] : "" // Ensure missing values are handled
                    });
                    return obj;
                }); 
            
                // document.getElementById('file_data').value = JSON.stringify(data);
                populateSearchFields(headers);
            };
            reader.readAsText(file);
                        

        } else {
            alert('Please select a CSV file.');
            event.target.value = '';
        }
    });

    
    function populateSearchFields(headers) {
        const dropdown = document.getElementById("search_field");
        dropdown.innerHTML = '<option value="" disabled selected>Select a field</option>';
    
        headers.forEach(header => {
            const option = document.createElement("option");
            option.value = header;
            option.textContent = header;
            dropdown.appendChild(option);
        });
    }
    
    document.getElementById('add_search_field').addEventListener('click', function() {
        const searchField = document.getElementById('search_field');
        const selectedField = searchField.options[searchField.selectedIndex];
        
        if (!selectedField.value) {
            alert('Please select a valid field first');
            return;
        }
    
        if ((savedFields.match(/,/g) || []).length >= 2) {
            alert('Maximum of 3 fields allowed');
            return;
        }
    
        if (savedFields === "") {
            savedFields = selectedField.textContent;
        } else {
            savedFields += ", " + selectedField.textContent;
        }
        
        updateSavedFieldsDisplay();
    });
    
    document.getElementById('reset_search_field').addEventListener('click', function() {
        savedFields = "";
        updateSavedFieldsDisplay();
    });
    
    function updateSavedFieldsDisplay() {
        const container = document.getElementById('saved_pairs_container');
        container.innerHTML = '';
        
        const fieldsArray = savedFields ? savedFields.split(", ") : [];
        
        fieldsArray.forEach((field, index) => {
            const fieldElement = document.createElement('div');
            fieldElement.className = 'saved-pair';
            fieldElement.innerHTML = `<span>${field}</span>
                <button type="button" class="remove-pair" data-index="${index}">×</button>`;
            container.appendChild(fieldElement);
        });
    
        document.querySelectorAll('.remove-pair').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                const fieldsArray = savedFields.split(", ");
                fieldsArray.splice(index, 1);
                savedFields = fieldsArray.join(", ");
                updateSavedFieldsDisplay();
            });
        });
    }
    
    document.querySelector('form').addEventListener('submit', function(event) {
        document.getElementById('selected_pairs_data').value = savedFields;
        console.log('Submitting fields:', savedFields);
    });