function guiCheckBox() {
    var guiCheckBox = document.getElementById("guis_avail");

    var guiOptions = document.getElementById("gui-options"); 
    var functionWordCheckBox = document.getElementById("clause_noun_verb_function");
    var wordnetCheckBox = document.getElementById("wordnet-classification-noun-verb"); 
    var searchWordCheckBox = document.getElementById("search_token_word_checkbox");
    var repfinderCheckBox = document.getElementById("repetition_finder"); 
    var sentComputeTabCheckBox = document.getElementById("compute_sentence_table"); 
    
    if(guiCheckBox.checked) {
        guiOptions.disabled = false;
        functionWordCheckBox.disabled = true;
        wordnetCheckBox.disabled = true;
        searchWordCheckBox.disabled = true;
        repfinderCheckBox.disabled = true;
        sentComputeTabCheckBox.disabled = true;
    } else {
        guiOptions.disabled = true;
        functionWordCheckBox.disabled = false;
        wordnetCheckBox.disabled = false;
        searchWordCheckBox.disabled = false;
        repfinderCheckBox.disabled = false;
        sentComputeTabCheckBox.disabled = false;
    }
}

function functionWordCheckBox() {
    var functionWordCheckBox = document.getElementById("clause_noun_verb_function");
    
    var functionWordOptions = document.getElementById("clause_noun_verb_function_options");
    var guiCheckBox = document.getElementById("guis_avail");
    var wordnetCheckBox = document.getElementById("wordnet-classification-noun-verb"); 
    var searchWordCheckBox = document.getElementById("search_token_word_checkbox");
    var repfinderCheckBox = document.getElementById("repetition_finder"); 
    var sentComputeTabCheckBox = document.getElementById("compute_sentence_table"); 

    if(functionWordCheckBox.checked) {
        functionWordOptions.disabled = false;
        guiCheckBox.disabled = true;
        wordnetCheckBox.disabled = true;
        searchWordCheckBox.disabled = true;
        repfinderCheckBox.disabled = true;
        sentComputeTabCheckBox.disabled = true;
    } else {
        functionWordOptions.disabled = true;
        guiCheckBox.disabled = false;
        wordnetCheckBox.disabled = false;
        searchWordCheckBox.disabled = false;
        repfinderCheckBox.disabled = false;
        sentComputeTabCheckBox.disabled = false;
    } 
} 

function wordnetCheckBox() {
    var wordnetCheckBox = document.getElementById("wordnet-classification-noun-verb"); 

    var guiCheckBox = document.getElementById("guis_avail");
    var functionWordCheckBox = document.getElementById("clause_noun_verb_function");
    var searchWordCheckBox = document.getElementById("search_token_word_checkbox");
    var repfinderCheckBox = document.getElementById("repetition_finder"); 
    var sentComputeTabCheckBox = document.getElementById("compute_sentence_table"); 

    if(wordnetCheckBox.checked) {
        guiCheckBox.disabled = true;
        functionWordCheckBox.disabled = true;
        searchWordCheckBox.disabled = true;
        repfinderCheckBox.disabled = true;
        sentComputeTabCheckBox.disabled = true;
    } else {
        guiCheckBox.disabled = false;
        functionWordCheckBox.disabled = false;
        searchWordCheckBox.disabled = false;
        repfinderCheckBox.disabled = false;
        sentComputeTabCheckBox.disabled = false;
    }
}

function searchWordCheckBox() {
    var searchWordCheckBox = document.getElementById("search_token_var");

    var searchWordText = document.getElementById("search-token-word-text");
    var guiCheckBox = document.getElementById("guis_avail");
    var conllSearchField = document.getElementById("conll_search_field");
    var wordnetCheckBox = document.getElementById("wordnet-classification-noun-verb"); 
    var functionWordCheckBox = document.getElementById("clause_noun_verb_function");
    var repfinderCheckBox = document.getElementById("repetition_finder"); 
    var sentComputeTabCheckBox = document.getElementById("compute_sentence_table"); 
    var postagOptions = document.getElementById("postag");
    var deprelOptions = document.getElementById("deprel");
    var postagBOptions = document.getElementById("postag_b");
    var deprelBOptions = document.getElementById("deprel_b");

    if(searchWordCheckBox.checked) { 
        searchWordText.disabled = false;
        conllSearchField.disabled = false;
        guiCheckBox.disabled = true;
        functionWordCheckBox.disabled = true;
        wordnetCheckBox.disabled = true;
        repfinderCheckBox.disabled = true;
        sentComputeTabCheckBox.disabled = true;
        postagOptions.disabled = false;
        deprelOptions.disabled =  false;
        postagBOptions.disabled = false;
        deprelBOptions.disabled = false;
    } else {
        searchWordText.disabled = true;
        conllSearchField.disabled = true;
        postagOptions.disabled = true;
        deprelOptions.disabled =  true;
        postagBOptions.disabled = true;
        deprelBOptions.disabled = true;
        guiCheckBox.disabled = false;
        functionWordCheckBox.disabled = false;
        wordnetCheckBox.disabled = false;
        repfinderCheckBox.disabled = false;
        sentComputeTabCheckBox.disabled = false;
    }
} 

function beginEndKSentenceCheckBox() {
    var repfinderCheckBox = document.getElementById("repetition_finder"); 
    var beginKsentencesNum = document.getElementById("begin-k-sentences");
    var endKsentencesNum = document.getElementById("end-k-sentences");

    var guiCheckBox = document.getElementById("guis_avail");
    var functionWordCheckBox = document.getElementById("clause_noun_verb_function");
    var wordnetCheckBox = document.getElementById("wordnet-classification-noun-verb"); 
    var searchWordCheckBox = document.getElementById("search_token_word_checkbox");
    var sentComputeTabCheckBox = document.getElementById("compute_sentence_table"); 

    if(repfinderCheckBox.checked) {
        beginKsentencesNum.disabled = false;
        endKsentencesNum.disabled = false;

        guiCheckBox.disabled = true;
        functionWordCheckBox.disabled = true;
        wordnetCheckBox.disabled = true;
        searchWordCheckBox.disabled = true;
        sentComputeTabCheckBox.disabled = true;
    } else {
        beginKsentencesNum.disabled = true;
        endKsentencesNum.disabled = true;

        guiCheckBox.disabled = false;
        functionWordCheckBox.disabled = false;
        wordnetCheckBox.disabled = false;
        searchWordCheckBox.disabled = false;
        sentComputeTabCheckBox.disabled = false;
    }
} 

function sentComputeTabCheckBox() {
    var sentComputeTabCheckBox = document.getElementById("compute_sentence_table");
    
    var guiCheckBox = document.getElementById("guis_avail");
    var repfinderCheckBox = document.getElementById("repetition_finder"); 
    var functionWordCheckBox = document.getElementById("clause_noun_verb_function");
    var wordnetCheckBox = document.getElementById("wordnet-classification-noun-verb"); 
    var searchWordCheckBox = document.getElementById("search_token_word_checkbox");
    var repfinderCheckBox = document.getElementById("repetition_finder"); 
    var sentComputeTabCheckBox = document.getElementById("compute_sentence_table"); 
    
    if(sentComputeTabCheckBox.checked) {
        guiCheckBox.disabled = true;
        repfinderCheckBox.disabled = true;
        functionWordCheckBox.disabled = true;
        wordnetCheckBox.disabled = true;
        searchWordCheckBox.disabled = true;
    } else {
        guiCheckBox.disabled = false;
        repfinderCheckBox.disabled = false;
        functionWordCheckBox.disabled = false;
        wordnetCheckBox.disabled = false;
        searchWordCheckBox.disabled = false;
    }

}

// document.getElementById("guis_avail").addEventListener("change", guiCheckBox);
// document.getElementById("clause_noun_verb_function").addEventListener("change", functionWordCheckBox);
// document.getElementById("wordnet-classification-noun-verb").addEventListener("change", wordnetCheckBox);
// document.getElementById("search_token_word_checkbox").addEventListener("change", searchWordCheckBox);
// document.getElementById("repetition_finder").addEventListener("change", beginEndKSentenceCheckBox);
// document.getElementById("compute_sentence_table").addEventListener("change", sentComputeTabCheckBox);

// commented out as there were errors in above code


//if none of the checkboxes are checked, alert the user when they click the run button and prevent the form from being submitted
document.getElementById("run-button")
    .addEventListener("click", function(event){
        const ids = [
            "clause_noun_verb_function",
            "wordnet-classification-noun-verb",
            "search_token_word_checkbox",
            "repetition_finder",
            "compute_sentence_table"
        ]
        let isChecked = false;

        for(let id of ids){
            const checkbox = document.getElementById(id);
            // console.log(`Checkbox with id ${id} is checked: ${checkbox.checked}`);
            if(checkbox.checked){
                isChecked = true;
                break;
            }
        }

        if(!isChecked){
            event.preventDefault();
            alert("Please select at least one option before running the analysis.");
        }
    })

    // Check fill in formats.
document.getElementById("run-button")
    .addEventListener("click", function(event){
        const functionWordCheckBox = document.getElementById("clause_noun_verb_function");
        const functionWordOptions = document.getElementById("clause_noun_verb_function_options");
        if(functionWordCheckBox.checked && functionWordOptions.value.trim() === "*"){
            event.preventDefault();
            alert("Please fill in the function word options field with the correct format.");
        }


        const searchWordCheckBox = document.getElementById("search_token_word_checkbox");
        const searchWordText = document.getElementById("search_kw");
        if(searchWordCheckBox.checked && searchWordText.value.trim() === ""){
            event.preventDefault();
            alert("Please fill in the search Token/Word text field.");
        }

    })



    // 1. 