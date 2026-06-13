
document.addEventListener("DOMContentLoaded", function () {

    let selectedFieldValues = []; 


    let savedPairsToSend = [];



    //<!--------------------------- Handle CSV Functions ---------------------!>
    //Populate dropdown based on uploaded CSV file
    document.getElementById("sunburst_file_input").addEventListener("change", function (event) {
        const file = event.target.files[0];
        
        // Check if the file is a CSV
        if (file && file.name.toLowerCase().endsWith('.csv')) {
            const reader = new FileReader();
            
            reader.onload = function () {
                const csvContent = reader.result;
                

                processCSV(csvContent);
                console.log("CSV File: ", csvContent)

            };
            
            reader.readAsText(file); // Start reading the file
        } else {
            alert('Please select a CSV file.');
            // Reset the file input
            event.target.value = '';
        }
    });

    function processCSV(csvContent) {
        const rows = csvContent.split("\n").map(row => row.split(","));
        if (rows.length < 2) return; // Ensure there's data

        const headers = rows[0];
        const data = rows.slice(1);

        populateDropdown(headers, data);
    }

    function populateDropdown(headers, data) {
        const dropdown = document.getElementById("search_field");
        dropdown.innerHTML = '<option value="" disabled selected>Select a field</option>';

        headers.forEach((header, index) => {
            const option = document.createElement("option");
            option.value =`${index}|${header}`
            // option.text = header
            // option.index = index
            option.text = header;
            option.textContent = header.trim();
            dropdown.appendChild(option);
        });

        dropdown.addEventListener("change", function () {
            const selectedIndex = this.value.split("|")[0]
            selectedFieldValues = getFieldData(selectedIndex, data); // Update the global array
            console.log('Selected Field Values:', selectedFieldValues); 
        });
    }

    function getFieldData(fieldIndex, data) {
        const values = data.map(row => {
            let cell = row[fieldIndex]; // Get the cell value at the specified column (fieldIndex)
        
            if (cell) {
                cell = cell.replace(/"/g, ""); // Remove all double quotes from the cell
                cell = cell.trim(); // Remove any leading or trailing whitespace
            } else {
                cell = ""; // Ensure cell is a string
            }
        
            return cell; // Return the cleaned cell value
        });

        // Filter out empty strings and get unique values
        const uniqueValues = [...new Set(values.filter(value => value !== ""))];
        
        populate_search_value_dropdown(uniqueValues);
        return uniqueValues;
    }    


    function populate_search_value_dropdown(uniqueValues) {
        const element  = document.getElementById("search_value_dropdown");
        element.options.length=0; 
        
        // for(let val of uniqueValues) {
        //     console.log(val);
        // }


        for(const value of uniqueValues) {
            const option = document.createElement("option");

            option.textContent = value;
            option.value = value; 

            element.appendChild(option);
        }
    }


    //<!-------------------- Search Value Functions ---------------------!> 
    const keywordInput = document.getElementById("keywordInput");
    const suggestionDropdown = document.getElementById("suggestion_dropdown");

    keywordInput.addEventListener("input", function () {
        const value = keywordInput.value;
        const lastChar = value[value.length - 1];
        let userInput = value.split(',').pop().trim().toLowerCase(); // Get the last value

        suggestionDropdown.innerHTML = ""; // Clear previous suggestions

        // Determine whether to show suggestions
        if (userInput || lastChar === ',') {
            let filteredValues;

            if (userInput) {
                filteredValues = selectedFieldValues.filter(val =>
                    val.toLowerCase().startsWith(userInput)
                );
            } else {
                // If userInput is empty and lastChar is a comma, show all suggestions
                filteredValues = selectedFieldValues;
            }

            if (filteredValues.length === 0) {
                // Show "no match" if no results are found
                const noMatch = document.createElement("div");
                noMatch.textContent = "No match";
                noMatch.style.fontStyle = "italic";
                noMatch.style.color = "gray";
                noMatch.classList.add("no-match");
                suggestionDropdown.appendChild(noMatch);
            } else {
                // Show up to 10 suggestions
                filteredValues.slice(0, 10).forEach(val => {
                    const suggestion = document.createElement("div");
                    suggestion.textContent = val;
                    suggestion.addEventListener("click", function () {
                        addValueToInput(val);
                    });
                    suggestionDropdown.appendChild(suggestion);
                });
            }

            suggestionDropdown.style.display = "block"; // Show dropdown
        } else {
            suggestionDropdown.style.display = "none"; // Hide dropdown
        }
    });

    // Hide dropdown if user clicks outside
    document.addEventListener("click", function (event) {
        if (!keywordInput.contains(event.target) && !suggestionDropdown.contains(event.target)) {
            suggestionDropdown.style.display = "none";
        }
    });

    function addValueToInput(value) {
        if (value.toLowerCase() === "no match") return; // Prevent adding "No match"
        let currentValues = keywordInput.value.split(',');
        currentValues = currentValues.map(val => val.trim()); // Clean up spaces

        currentValues[currentValues.length - 1] = value;

        keywordInput.value = currentValues.filter(val => val).join(", ") + ", ";
        keywordInput.focus(); // Bring focus back to the input

        suggestionDropdown.style.display = "none"; // Hide dropdown
    }

    // New functionality: Add Filter Option and CSV Field List Pair
    document.getElementById('add_pair_button').addEventListener('click', function() {
        const searchFieldDropdown = document.getElementById('search_field');
        const csvFieldListInput = document.getElementById('keywordInput');
        const savedPairsContainer = document.getElementById('saved_pairs_container');

        // const searchField = searchFieldDropdown.options[searchFieldDropdown.selectedIndex].text.trim();
        const searchField = document.getElementById("search_field")
        let field = search_field.value.split('|')[1];


        let csvFieldList = csvFieldListInput.value.trim();
        if (csvFieldList.endsWith(",")) {
            csvFieldList = csvFieldList.slice(0, -1); // Remove the trailing comma
        }


        // Check if CSV Field List contains more than 2 words separated by commas
        const csvFieldWords = csvFieldList.split(',').map(word => word.trim()).filter(word => word.length > 0);
        if (csvFieldWords.length <= 2) {
            alert('The CSV Field List must contain more than 2 words separated by commas.');
            return; // Stop execution if validation fails
        }

        if (field && csvFieldList) {
            // Save the pair

            const pair = [`${field}|`+ csvFieldList]


            add_to_saved_pairs_ui(field, csvFieldList);

            csvFieldListInput.value = '';
        } else {
            alert('Please select a Search Field and enter a CSV Field List.');
        }
    });



    //<!------------------Full Field Visualization Functions -----------------------!>
    
     document.getElementById('visualize_full_field').addEventListener('click', function() {
        let search_field = document.getElementById("search_field")
        
        field = search_field.value.split('|')[1];

        if(field == undefined) {
            alert("The search field option is empty. Please, select a field.");
        } else {
            add_to_saved_pairs_ui(field, [])
        }

    })


    function add_to_saved_pairs_ui(field, values) {
        saved_pairs = document.getElementById("saved_pairs_container");
        
        let label = document.getElementById("saved_pairs_ui_label")
        if(!label) {
            label = document.createElement('div')
            label.id = "saved_pairs_ui_label";
            saved_pairs.appendChild(label);
        }

        let ui_pair = ""

        //NOTE: This is NOT how they should be passed in the backend. There should be no space between field|value1, value2, etc, this is simply for UI purposes. 
        if(values.length > 0){ 
            ui_pair = field + "| " + values;
            
            for_backend = [field + "|" + values];
            savedPairsToSend.push(for_backend);

            
        } else {
            ui_pair = field + "| ALL"
            for_backend = [field + "|"];
            savedPairsToSend.push(for_backend);
        }

        if(label.textContent == "") {
            label.textContent = ui_pair;
        } else {
            label.textContent = label.textContent + `, ${ui_pair}`
        }
        // Clear the input field for CSV Field List
        // csvFieldListInput.value = '';
    }


    //<!------------- Handle Form Submission -----------------!>
    document.querySelector('.sentiment-analysis-form').addEventListener('submit', function() {
        document.getElementById('savedPairsToSend').value = JSON.stringify(savedPairsToSend);
        // console.log("SENDING " + JSON.stringify(savedPairsToSend));
    });

});
