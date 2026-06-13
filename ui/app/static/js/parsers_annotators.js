document.addEventListener("DOMContentLoaded", function() {
    const parserCheckbox = document.getElementById("parsers_var");
    const annotatorCheckbox = document.getElementById("annotators_var");
    const parserDropdown = document.getElementById("parser_menu_var");
    const annotatorDropdown = document.getElementById("annotators_menu_var");

    function updateDropdowns() {
        parserDropdown.disabled = !parserCheckbox.checked;
        annotatorDropdown.disabled = !annotatorCheckbox.checked;
    }

    updateDropdowns();
    parserCheckbox.addEventListener("change", updateDropdowns);
    annotatorCheckbox.addEventListener("change", updateDropdowns);
});

var parsers_var = document.getElementById("parsers_var");
var parser_menu_var = document.getElementById("parser_menu_var");
var annotators_var = document.getElementById("annotators_var");
var annotators_menu_var = document.getElementById("annotators_menu_var");

parsers_var.addEventListener('change',function() {
    annotators_var.disabled = this.checked;
    annotators_menu_var.disabled = this.checked;
    if(this.checked){
        annotators_var.checked = false;            
    }
});


annotators_var.addEventListener('change',function() {
    parsers_var.disabled = this.checked;
    parser_menu_var.disabled = this.checked;
    if(this.checked){
        parsers_var.checked = false;
    }
});

function loadHelper(){
    if(parsers_var.checked){
        annotators_var.disabled = true;
        annotators_menu_var.disabled = true;
    }
    if(annotators_var.checked){
        parsers_var.disabled = true;
        parser_menu_var.disabled = true;
    }
}

//write a function here 


loadHelper();