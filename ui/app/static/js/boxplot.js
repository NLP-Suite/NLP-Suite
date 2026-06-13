// Populate the field dropdowns from the uploaded CSV's header row and stash
// the raw CSV text in the hidden inputFileData field the agent reads.
const fieldSelects = [
    document.getElementById("csv_field_visualization"),
    document.getElementById("boxplot_csv_split"),
    document.getElementById("boxplot_csv_color"),
];

document.getElementById("boxplot_input_yaxis").addEventListener("change", function (event) {
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
    };
    reader.readAsText(file);
});

function populateDropdowns(csvContent) {
    const firstLine = csvContent.split("\n")[0];
    if (!firstLine) return;
    const headers = firstLine.split(",").map((h) => h.trim().replace(/^"|"$/g, ""));

    fieldSelects.forEach(function (dropdown) {
        dropdown.innerHTML = '<option value="" disabled selected>Select a field</option>';
        headers.forEach(function (header) {
            const option = document.createElement("option");
            option.value = header;
            option.textContent = header;
            dropdown.appendChild(option);
        });
    });
}

document.querySelector(".boxplot-form").addEventListener("submit", function (event) {
    if (!document.getElementById("inputFileData").value) {
        alert("Please select a CSV file first.");
        event.preventDefault();
    }
});
