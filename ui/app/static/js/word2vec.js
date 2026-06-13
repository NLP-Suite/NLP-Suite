// WSI, BERT word embeddings, and Gensim Word2Vec are mutually exclusive; the
// Gensim hyperparameters only apply to the Gensim path.
var wordSenseInduction = document.getElementById("WSI_var");
var wordEmbeddingsBERT = document.getElementById("BERT_var");
var word2VecGensim = document.getElementById("Gensim_var");
var trainingModelArchitecture = document.getElementById("sg_menu_var");
var vectorSize = document.getElementById("vector_size_var");
var windowSize = document.getElementById("window_var");
var minCount = document.getElementById("min_count_var");
var visualizationOptionVector = document.getElementById("vis_menu_var");
var visualizationOptionDimension = document.getElementById("dim_menu_var");

wordSenseInduction.addEventListener("change", function () {
    wordEmbeddingsBERT.disabled = this.checked;
    word2VecGensim.disabled = this.checked;
    trainingModelArchitecture.disabled = this.checked;
    vectorSize.disabled = this.checked;
    windowSize.disabled = this.checked;
    minCount.disabled = this.checked;

    if (this.checked) {
        wordEmbeddingsBERT.checked = false;
        word2VecGensim.checked = false;
    }
});

wordEmbeddingsBERT.addEventListener("change", function () {
    wordSenseInduction.disabled = this.checked;
    word2VecGensim.disabled = this.checked;
    trainingModelArchitecture.disabled = this.checked;
    vectorSize.disabled = this.checked;
    windowSize.disabled = this.checked;
    minCount.disabled = this.checked;

    if (this.checked) {
        wordSenseInduction.checked = false;
        word2VecGensim.checked = false;
    }
});

word2VecGensim.addEventListener("change", function () {
    wordEmbeddingsBERT.disabled = this.checked;
    wordSenseInduction.disabled = this.checked;

    if (this.checked) {
        wordEmbeddingsBERT.checked = false;
        wordSenseInduction.checked = false;
    }
});

visualizationOptionVector.addEventListener("change", function () {
    if (this.value === "Do not plot") {
        visualizationOptionDimension.disabled = true;
    } else {
        visualizationOptionDimension.value = "2D";
        visualizationOptionDimension.disabled = false;
    }
});
