function guiCheckBox() {
    var computeNgrams = document.getElementById("Ngrams_compute_var");
    var ngramType = document.getElementById("ngrams_menu_var");
    var ngramSize = document.getElementById("ngrams_size");
    var ngramOptions = document.getElementById("ngrams_options_list");
    var optionPlusBox = document.getElementsByName("options-+")[0];
    var optionResetBox = document.getElementsByName("options-reset")[0];
    var optionShowBox = document.getElementsByName("options-show")[0];
    var searchWordsBox = document.getElementById("search_words");
    var searchWordsMinusK = document.getElementById("minus_K_words_var");
    var searchWordsPlusK = document.getElementById("plus_K_words_var");
    var searchOptions = document.getElementById("viewer_options_list");
    var searchOptionsButtons = document.getElementsByName("search-options-+")[0];
    var searchOptionsResetButton = document.getElementsByName("search-options-reset")[0];
    var searchOptionsShowButton = document.getElementsByName("search-options-show")[0];
    // csv_file_var is permanently disabled (coming soon) and not toggled here
    var ngramViewerCheckbox = document.getElementById("ngrams_viewer_var");
    var coOccurCheckbox = document.getElementById("CoOcc_Viewer_var");
    var dateOptions = document.getElementById("date_options");
    var aggregateDropdown = document.getElementById("temporal_aggregation_var");


    if (computeNgrams.checked) {
        ngramType.disabled = false;
        ngramSize.disabled = false;
        ngramOptions.disabled = false;
        optionPlusBox.disabled = false;
        optionResetBox.disabled = false;
        optionShowBox.disabled = false;
        searchWordsBox.disabled = false;
        searchWordsMinusK.disabled = false;
        searchWordsPlusK.disabled = false;
        searchOptions.disabled = false;
        searchOptionsButtons.disabled = false;
        searchOptionsResetButton.disabled = false;
        searchOptionsShowButton.disabled = false;
        ngramViewerCheckbox.disabled = true;
        coOccurCheckbox.disabled = true;
        dateOptions.disabled = false;
        aggregateDropdown.disabled = false;


    } else {
        ngramType.disabled = true;
        ngramSize.disabled = true;
        ngramOptions.disabled = true;
        optionPlusBox.disabled = true;
        optionResetBox.disabled = true;
        optionShowBox.disabled = true;
        searchWordsBox.disabled = true;
        searchWordsMinusK.disabled = true;
        searchWordsPlusK.disabled = true;
        searchOptions.disabled = true;
        searchOptionsButtons.disabled = true;
        searchOptionsResetButton.disabled = true;
        searchOptionsShowButton.disabled = true;
        ngramViewerCheckbox.disabled = false;
        coOccurCheckbox.disabled = false;
        dateOptions.disabled = true;
        aggregateDropdown.disabled = true;
        dateOptions.checked = false;

        }
    }


    function toggleGuiDropdown() {
        var guiCheckbox = document.getElementById("guis_avail");
        var guiDropdown = document.getElementById("gui-options");
        guiDropdown.disabled = !guiCheckbox.checked;
    }

    function toggleNGramDropdown() {
        var ngramCheckbox = document.getElementById("compute-ngrams");
        var ngramDropdown = document.getElementById("compute_n-gram_options");
        ngramDropdown.disabled = !ngramCheckbox.checked;
    }

    function toggleCoOccurrenceOptions() {
        var guiCheckbox = document.getElementById("guis_avail");
        var ngramCheckbox = document.getElementById("compute-ngrams");
        var coOccurCheckbox = document.getElementById("co-occurrences-viewer");
        var coOccurWithinSenCheckbox = document.getElementById("co-occurrence-within-sen");
        var searchOptDropdown = document.getElementById("search-options-dropdown");
        var dateOptions = document.getElementById("date-options");
        var aggregateDropdown = document.getElementById("aggregate-dropdown");
        var dateLabel = document.getElementById("date-option-label");

        coOccurWithinSenCheckbox.disabled = !coOccurCheckbox.checked;
        searchOptDropdown.disabled = !coOccurCheckbox.checked;
        dateOptions.disabled = !coOccurCheckbox.checked;
        aggregateDropdown.disabled = !coOccurCheckbox.checked || !dateOptions.checked;
        guiCheckbox.disabled = coOccurCheckbox.checked;
        ngramCheckbox.disabled = coOccurCheckbox.checked;

        if (dateOptions.checked) {
            dateLabel.innerText = "Date option ON";
        } else {
            dateLabel.innerText = "Date option OFF";
        }
    } 

    document.getElementById("Ngrams_compute_var").addEventListener("change", guiCheckBox);
    guiCheckBox(); // prolly unnecessary ?

    // document.getElementById("guis_avail").addEventListener("change", toggleGuiDropdown);
    // toggleGuiDropdown();
    
    // document.getElementById("compute-ngrams").addEventListener("change", toggleNGramDropdown);
    // toggleNGramDropdown();

    // document.getElementById("co-occurrences-viewer").addEventListener("change", toggleCoOccurrenceOptions);
    // toggleCoOccurrenceOptions();
    // document.getElementById("date-options").addEventListener("change", toggleCoOccurrenceOptions);

function listofitems1() {
  var optionsSelect = document.getElementById("viewer_options_list");
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

listofitems1();

