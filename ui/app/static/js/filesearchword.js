function listofitems3() {
  var optionsSelect = document.getElementById("search_options");
  var pickedSelect = document.getElementById("optionss");
  var plusbutton = document.getElementsByName("search-options-+")[0];
  var resetbutton = document.getElementsByName("search-options-reset")[0];
  var minusbutton = document.getElementsByName("search-options-show")[0];

  if (optionsSelect && pickedSelect && plusbutton && resetbutton && minusbutton) {
    plusbutton.onclick = function () {
      var temp = optionsSelect.options[optionsSelect.selectedIndex];
      var opt = document.createElement("option");
      opt.value = temp.value;
      opt.text = temp.text;
      pickedSelect.add(opt);
    };

    minusbutton.onclick = function () {
      if (pickedSelect.selectedIndex >= 0) {
        pickedSelect.remove(pickedSelect.selectedIndex);
      }
    };

    resetbutton.onclick = function () {
      pickedSelect.length = 0;
    };
  }
}

listofitems3();


// The endpoint wants exactly one search mode: dictionary mode enables its file
// picker, keyword mode enables the term/±K/sentence-extraction controls.
var searchCorpusByDictionary = document.getElementById("search_by_dictionary");
var searchCorpusByWords = document.getElementById("search_by_keyword");
var searchOptionSelected = document.getElementById("search_options");
var userInput = document.getElementById("search_keyword_values");
var minusK = document.getElementById("minus_K_words_sentences_var");
var plusK = document.getElementById("plus_K_words_sentences_var");
var fileName = document.getElementById("selectedCsvFile");
var dictionaryFileButton = document.getElementById("selectDictionaryFile");
var extractKSentences = document.getElementById("extract_sentences_var");
var coOccurringCommas = document.getElementById("coOccurring_keywords_var");
var createSubcorpus = document.getElementById("create_subcorpus_var");

function syncSearchModeControls() {
    var byDictionary = searchCorpusByDictionary.checked;
    var byWords = searchCorpusByWords.checked;

    searchCorpusByDictionary.disabled = byWords;
    searchCorpusByWords.disabled = byDictionary;

    dictionaryFileButton.disabled = !byDictionary;
    fileName.disabled = !byDictionary;

    userInput.disabled = !byWords;
    extractKSentences.disabled = !byWords;
    coOccurringCommas.disabled = !byWords;
    createSubcorpus.disabled = !byWords;
    if (!byWords) {
        extractKSentences.checked = false;
        coOccurringCommas.checked = false;
        createSubcorpus.checked = false;
    }

    var withinSentence = searchOptionSelected.value !== "Search within document";
    plusK.disabled = !(byWords && withinSentence);
    minusK.disabled = !(byWords && withinSentence);
    if (byWords && !withinSentence) {
        extractKSentences.disabled = true;
        extractKSentences.checked = false;
    }
}

searchCorpusByDictionary.addEventListener("change", syncSearchModeControls);
searchCorpusByWords.addEventListener("change", syncSearchModeControls);
searchOptionSelected.addEventListener("change", syncSearchModeControls);
syncSearchModeControls();



function submitbutton2() {
  var sel1 = document.getElementById("optionss");

  var out1 = "[";
  for (var i = 0; i < sel1.options.length; i++) {
    out1 = out1 + '"' + sel1.options[i].value + '"';
    if (i < sel1.options.length - 1) out1 = out1 + ",";
  }
  out1 = out1 + "]";

  document.getElementById("search_options_hidden_list").value = out1;

  return true;
}



