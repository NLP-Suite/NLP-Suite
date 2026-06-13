function zoomInDownCheckbox() {
    var zoomInDownCheckbox = document.getElementById("zoom-in-related-words");
    var yourSynsetDropdown = document.getElementById("your-synset");

    var annotateCorpusCheckbox = document.getElementById("annotate-corpus-checkbox");
    var extractProperNounCheckbox = document.getElementById("extract-proper-noun-checkbox");
    var extractImproperNounCheckbox = document.getElementById("extract-improper-noun-checkbox");
    var zoomOutUpCheckbox = document.getElementById("zoom-out-up");
    var extractNounVerbCheckbox = document.getElementById("extract-noun-verb-conll");
    var classifyAggregateInputCheckbox = document.getElementById("zoom-out-classify-aggregate-input");
    var zoomOutSentenceIdCheckbox = document.getElementById("zoom-out-sentenceID"); 

    if(zoomInDownCheckbox.checked) {
        yourSynsetDropdown.disabled = false;

        annotateCorpusCheckbox.disabled = true;
        extractProperNounCheckbox.disabled = true;
        extractImproperNounCheckbox.disabled = true;
        zoomOutUpCheckbox.disabled = true;
        extractNounVerbCheckbox.disabled = true;
        classifyAggregateInputCheckbox.disabled = true;
        zoomOutSentenceIdCheckbox.disabled = true;
    } else {
        yourSynsetDropdown.disabled = true;

        annotateCorpusCheckbox.disabled = false;
        extractProperNounCheckbox.disabled = false;
        extractImproperNounCheckbox.disabled = false;
        zoomOutUpCheckbox.disabled = false;
        extractNounVerbCheckbox.disabled = false;
        classifyAggregateInputCheckbox.disabled = false;
        zoomOutSentenceIdCheckbox.disabled = false;
    }
}  

function annotateCorpusCheckbox() {
    var annotateCorpusCheckbox = document.getElementById("annotate-corpus-checkbox");

    var zoomInDownCheckbox = document.getElementById("zoom-in-related-words");
    var extractProperNounCheckbox = document.getElementById("extract-proper-noun-checkbox");
    var extractImproperNounCheckbox = document.getElementById("extract-improper-noun-checkbox");
    var zoomOutUpCheckbox = document.getElementById("zoom-out-up");
    var extractNounVerbCheckbox = document.getElementById("extract-noun-verb-conll");
    var classifyAggregateInputCheckbox = document.getElementById("zoom-out-classify-aggregate-input");
    var zoomOutSentenceIdCheckbox = document.getElementById("zoom-out-sentenceID"); 

    if(annotateCorpusCheckbox.checked) {
        zoomInDownCheckbox.disabled = true;
        extractProperNounCheckbox.disabled = true;
        extractImproperNounCheckbox.disabled = true;
        zoomOutUpCheckbox.disabled = true;
        extractNounVerbCheckbox.disabled = true;
        classifyAggregateInputCheckbox.disabled = true;
        zoomOutSentenceIdCheckbox.disabled = true;
    } else {
        zoomInDownCheckbox.disabled = false;
        extractProperNounCheckbox.disabled = false;
        extractImproperNounCheckbox.disabled = false;
        zoomOutUpCheckbox.disabled = false;
        extractNounVerbCheckbox.disabled = false;
        classifyAggregateInputCheckbox.disabled = false;
        zoomOutSentenceIdCheckbox.disabled = false;
    }
}  

function extractProperNounCheckbox() {
    var extractProperNounCheckbox = document.getElementById("extract-proper-noun-checkbox");
    
    var zoomInDownCheckbox = document.getElementById("zoom-in-related-words");
    var annotateCorpusCheckbox = document.getElementById("annotate-corpus-checkbox");
    var extractImproperNounCheckbox = document.getElementById("extract-improper-noun-checkbox");
    var zoomOutUpCheckbox = document.getElementById("zoom-out-up");
    var extractNounVerbCheckbox = document.getElementById("extract-noun-verb-conll");
    var classifyAggregateInputCheckbox = document.getElementById("zoom-out-classify-aggregate-input");
    var zoomOutSentenceIdCheckbox = document.getElementById("zoom-out-sentenceID"); 

    if(extractProperNounCheckbox.checked) {
        zoomInDownCheckbox.disabled = true;
        extractImproperNounCheckbox.disabled = true;
        annotateCorpusCheckbox.disabled = true;
        zoomOutUpCheckbox.disabled = true;
        extractNounVerbCheckbox.disabled = true;
        classifyAggregateInputCheckbox.disabled = true;
        zoomOutSentenceIdCheckbox.disabled = true;
    } else {
        zoomInDownCheckbox.disabled = false;
        extractImproperNounCheckbox.disabled = false;
        annotateCorpusCheckbox.disabled = false;
        zoomOutUpCheckbox.disabled = false;
        extractNounVerbCheckbox.disabled = false;
        classifyAggregateInputCheckbox.disabled = false;
        zoomOutSentenceIdCheckbox.disabled = false;
    }
}  

function extractImproperNounCheckbox() {
    var extractImproperNounCheckbox = document.getElementById("extract-improper-noun-checkbox");

    var extractProperNounCheckbox = document.getElementById("extract-proper-noun-checkbox");
    var zoomInDownCheckbox = document.getElementById("zoom-in-related-words");
    var annotateCorpusCheckbox = document.getElementById("annotate-corpus-checkbox");
    var zoomOutUpCheckbox = document.getElementById("zoom-out-up");
    var extractNounVerbCheckbox = document.getElementById("extract-noun-verb-conll");
    var classifyAggregateInputCheckbox = document.getElementById("zoom-out-classify-aggregate-input");
    var zoomOutSentenceIdCheckbox = document.getElementById("zoom-out-sentenceID"); 

    if(extractImproperNounCheckbox.checked) {
        zoomInDownCheckbox.disabled = true;
        extractProperNounCheckbox.disabled = true;
        annotateCorpusCheckbox.disabled = true;
        extractNounVerbCheckbox.disabled = true;
        zoomOutUpCheckbox.disabled = true;
        classifyAggregateInputCheckbox.disabled = true;
        zoomOutSentenceIdCheckbox.disabled = true;
    } else {
        zoomInDownCheckbox.disabled = false;
        extractProperNounCheckbox.disabled = false;
        annotateCorpusCheckbox.disabled = false;
        zoomOutUpCheckbox.disabled = false;
        extractNounVerbCheckbox.disabled = false;
        classifyAggregateInputCheckbox.disabled = false;
        zoomOutSentenceIdCheckbox.disabled = false;
    }
}



function extractZoomOutUpCheckbox(){
    var zoomOutUpCheckbox = document.getElementById("zoom-out-up");
    var extractImproperNounCheckbox = document.getElementById("extract-improper-noun-checkbox");

    var extractProperNounCheckbox = document.getElementById("extract-proper-noun-checkbox");
    var zoomInDownCheckbox = document.getElementById("zoom-in-related-words");
    var annotateCorpusCheckbox = document.getElementById("annotate-corpus-checkbox");
    
    var extractNounVerbCheckbox = document.getElementById("extract-noun-verb-conll");
    var classifyAggregateInputCheckbox = document.getElementById("zoom-out-classify-aggregate-input");
    var zoomOutSentenceIdCheckbox = document.getElementById("zoom-out-sentenceID");

    if(zoomOutUpCheckbox.checked) {
        zoomInDownCheckbox.disabled = true;
        extractProperNounCheckbox.disabled = true;
        annotateCorpusCheckbox.disabled = true;
        extractNounVerbCheckbox.disabled = true;
        classifyAggregateInputCheckbox.disabled = true;
        zoomOutSentenceIdCheckbox.disabled = true;
        extractImproperNounCheckbox.disabled = true;
    }else{
        zoomInDownCheckbox.disabled = false;
        extractProperNounCheckbox.disabled = false;
        annotateCorpusCheckbox.disabled = false;
        extractNounVerbCheckbox.disabled = false;
        classifyAggregateInputCheckbox.disabled = false;
        zoomOutSentenceIdCheckbox.disabled = false;
        extractImproperNounCheckbox.disabled = false;

    }

}

function extractNounVerbCheck(){
    var extractNounVerbCheckbox = document.getElementById("extract-noun-verb-conll");
    var zoomOutUpCheckbox = document.getElementById("zoom-out-up");
    var extractImproperNounCheckbox = document.getElementById("extract-improper-noun-checkbox");

    var extractProperNounCheckbox = document.getElementById("extract-proper-noun-checkbox");
    var zoomInDownCheckbox = document.getElementById("zoom-in-related-words");
    var annotateCorpusCheckbox = document.getElementById("annotate-corpus-checkbox");
    
    
    var classifyAggregateInputCheckbox = document.getElementById("zoom-out-classify-aggregate-input");
    var zoomOutSentenceIdCheckbox = document.getElementById("zoom-out-sentenceID");

    if(extractNounVerbCheckbox.checked) {
        zoomInDownCheckbox.disabled = true;
        extractProperNounCheckbox.disabled = true;
        annotateCorpusCheckbox.disabled = true;
        classifyAggregateInputCheckbox.disabled = true;
        zoomOutSentenceIdCheckbox.disabled = true;
        extractImproperNounCheckbox.disabled = true;
        zoomOutUpCheckbox.disabled = true;
    }else{
        zoomInDownCheckbox.disabled = false;
        extractProperNounCheckbox.disabled = false;
        annotateCorpusCheckbox.disabled = false;
        classifyAggregateInputCheckbox.disabled = false;
        zoomOutSentenceIdCheckbox.disabled = false;
        extractImproperNounCheckbox.disabled = false;
        zoomOutUpCheckbox.disabled = false;

    }

}

function zoomOutClassify(){
    var extractNounVerbCheckbox = document.getElementById("extract-noun-verb-conll");
    var zoomOutUpCheckbox = document.getElementById("zoom-out-up");
    var extractImproperNounCheckbox = document.getElementById("extract-improper-noun-checkbox");

    var extractProperNounCheckbox = document.getElementById("extract-proper-noun-checkbox");
    var zoomInDownCheckbox = document.getElementById("zoom-in-related-words");
    var annotateCorpusCheckbox = document.getElementById("annotate-corpus-checkbox");
    
    
    var classifyAggregateInputCheckbox = document.getElementById("zoom-out-classify-aggregate-input");
    var zoomOutSentenceIdCheckbox = document.getElementById("zoom-out-sentenceID");

    if(classifyAggregateInputCheckbox.checked) {
        zoomInDownCheckbox.disabled = true;
        extractProperNounCheckbox.disabled = true;
        annotateCorpusCheckbox.disabled = true;
        extractNounVerbCheckbox.disabled = true;
        zoomOutSentenceIdCheckbox.disabled = true;
        extractImproperNounCheckbox.disabled = true;
        zoomOutUpCheckbox.disabled = true;
    }else{
        zoomInDownCheckbox.disabled = false;
        extractProperNounCheckbox.disabled = false;
        annotateCorpusCheckbox.disabled = false;
        extractNounVerbCheckbox.disabled = false;
        zoomOutSentenceIdCheckbox.disabled = false;
        extractImproperNounCheckbox.disabled = false;
        zoomOutUpCheckbox.disabled = false;

    }

}

function zoomOutSentenceID(){
    var extractNounVerbCheckbox = document.getElementById("extract-noun-verb-conll");
    var zoomOutUpCheckbox = document.getElementById("zoom-out-up");
    var extractImproperNounCheckbox = document.getElementById("extract-improper-noun-checkbox");

    var extractProperNounCheckbox = document.getElementById("extract-proper-noun-checkbox");
    var zoomInDownCheckbox = document.getElementById("zoom-in-related-words");
    var annotateCorpusCheckbox = document.getElementById("annotate-corpus-checkbox");
    
    
    var classifyAggregateInputCheckbox = document.getElementById("zoom-out-classify-aggregate-input");
    var zoomOutSentenceIdCheckbox = document.getElementById("zoom-out-sentenceID");

    var dictWordNetInput = document.getElementById("wordnet-classified-aggregated-csv");

    if(zoomOutSentenceIdCheckbox.checked) {
        dictWordNetInput.disabled = false;
        zoomInDownCheckbox.disabled = true;
        extractProperNounCheckbox.disabled = true;
        annotateCorpusCheckbox.disabled = true;
        extractNounVerbCheckbox.disabled = true;
        classifyAggregateInputCheckbox.disabled = true;
        extractImproperNounCheckbox.disabled = true;
        zoomOutUpCheckbox.disabled = true;
    }else{
        dictWordNetInput.disabled = true;
        zoomInDownCheckbox.disabled = false;
        extractProperNounCheckbox.disabled = false;
        annotateCorpusCheckbox.disabled = false;
        extractNounVerbCheckbox.disabled = false;
        classifyAggregateInputCheckbox.disabled = false;
        extractImproperNounCheckbox.disabled = false;
        zoomOutUpCheckbox.disabled = false;

    }

}


document.getElementById("zoom-in-related-words").addEventListener("change", zoomInDownCheckbox);
document.getElementById("annotate-corpus-checkbox").addEventListener("change", annotateCorpusCheckbox);
document.getElementById("extract-proper-noun-checkbox").addEventListener("change", extractProperNounCheckbox);
document.getElementById("extract-improper-noun-checkbox").addEventListener("change", extractImproperNounCheckbox);
document.getElementById("zoom-out-up").addEventListener("change", extractZoomOutUpCheckbox);
document.getElementById("extract-noun-verb-conll").addEventListener("change", extractNounVerbCheck);
document.getElementById("zoom-out-classify-aggregate-input").addEventListener("change", zoomOutClassify);
document.getElementById("zoom-out-sentenceID").addEventListener("change", zoomOutSentenceID);

