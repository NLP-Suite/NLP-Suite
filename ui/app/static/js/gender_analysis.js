// The CoreNLP and dictionary annotators are mutually exclusive; the dictionary
// path enables its file-path input and pronoun option. The US SS plot option is
// permanently disabled (coming soon) — its controls are never enabled here.
function coreNlpGenAnnotateCheckbox() {
    var coreNlpGenAnnotateCheckbox = document.getElementById("CoreNLP_gender_annotator_var");
    var annotatorDictCheckbox = document.getElementById("annotator_dictionary_var");

    annotatorDictCheckbox.disabled = coreNlpGenAnnotateCheckbox.checked;
}

function annotateGenderCheckbox() {
    var coreNlpGenAnnotateCheckbox = document.getElementById("CoreNLP_gender_annotator_var");
    var annotatorDictCheckbox = document.getElementById("annotator_dictionary_var");
    var selectDicFile = document.getElementById("select-dic-file");
    var personalPronouns = document.getElementById("personal_pronouns_var");

    if (annotatorDictCheckbox.checked) {
        coreNlpGenAnnotateCheckbox.disabled = true;
        selectDicFile.disabled = false;
        personalPronouns.disabled = false;
    } else {
        coreNlpGenAnnotateCheckbox.disabled = false;
        selectDicFile.disabled = true;
        personalPronouns.disabled = true;
    }
}

document.getElementById("CoreNLP_gender_annotator_var").addEventListener("change", coreNlpGenAnnotateCheckbox);
document.getElementById("annotator_dictionary_var").addEventListener("change", annotateGenderCheckbox);
