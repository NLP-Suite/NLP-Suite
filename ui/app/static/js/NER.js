function nerToggle(){
    var packagesOption = document.getElementById("ner_algorithm");
    var tagsOption = document.getElementById("ner_tags");
    var buttonSel = document.getElementById("button_id");
    var resetID = document.getElementById("reset_id");
    var nerList = document.getElementById("ner_list");
    if(packagesOption.value === "Stanford CoreNLP"){
        tagsOption.disabled = false;
        buttonSel.disabled = false;
        resetID.disabled = false;
        nerList.disabled = false;
    }
    else{
        tagsOption.disabled = true;
        buttonSel.disabled = true;
        resetID.disabled = true;
        nerList.disabled = true;
    }
}
document.getElementById("ner_algorithm").addEventListener("change", nerToggle);
nerToggle();

function nerAddTag(){
    var tagsOption = document.getElementById("ner_tags");
    var nerList = document.getElementById("ner_list");
    // aggregate options ("All social actors", ...) carry comma-separated tag lists
    var values = tagsOption.options[tagsOption.selectedIndex].value.split(",");
    var current = nerList.value ? nerList.value.split(",") : [];
    values.forEach(function(value){
        if(current.indexOf(value) === -1){
            current.push(value);
        }
    });
    nerList.value = current.join(",");
}
document.getElementById("button_id").addEventListener("click", nerAddTag);

function nerResetTags(){
    document.getElementById("ner_list").value = "";
}
document.getElementById("reset_id").addEventListener("click", nerResetTags);
