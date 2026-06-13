// Populate the field dropdowns from the uploaded CSV's header row, stash the
// raw CSV text in the hidden inputFileData field, and build the Y-axis field
// list as the JSON array the agent's /excel_charts endpoint parses.
const headerSelects = [
    document.getElementById("csv_field_visualization"),
    document.getElementById("x-axis"),
    document.getElementById("addY-axis"),
];
let yAxisFields = [];

document.getElementById("excel_charts_file_input").addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (!file || !file.name.toLowerCase().endsWith(".csv")) {
        alert("Please select a CSV file.");
        event.target.value = "";
        return;
    }
    const reader = new FileReader();
    reader.onload = function () {
        const csvContent = reader.result;
        document.getElementById("inputFileData").value = csvContent;
        populateDropdowns(csvContent);
        resetYAxis();
    };
    reader.readAsText(file);
});

function populateDropdowns(csvContent) {
    const firstLine = csvContent.split("\n")[0];
    if (!firstLine) return;
    const headers = firstLine.split(",").map((h) => h.trim().replace(/^"|"$/g, ""));

    headerSelects.forEach(function (dropdown) {
        dropdown.innerHTML = '<option value="" disabled selected>Select a field</option>';
        headers.forEach(function (header) {
            const option = document.createElement("option");
            option.value = header;
            option.textContent = header;
            dropdown.appendChild(option);
        });
    });
}

function syncYAxis() {
    document.getElementById("csv_file_field_Y_axis_list").value = JSON.stringify(yAxisFields);
    document.getElementById("y_axis_display").value = yAxisFields.join(", ");
}

function resetYAxis() {
    yAxisFields = [];
    syncYAxis();
}

document.getElementById("add_y_axis_button").addEventListener("click", function () {
    const select = document.getElementById("addY-axis");
    const value = select.value;
    if (value && yAxisFields.indexOf(value) === -1) {
        yAxisFields.push(value);
        syncYAxis();
    }
});

document.getElementById("reset_y_axis_button").addEventListener("click", resetYAxis);

document.querySelector(".excel-plotly-charts-form").addEventListener("submit", function (event) {
    if (!document.getElementById("inputFileData").value) {
        alert("Please select a CSV file first.");
        event.preventDefault();
    }
});
