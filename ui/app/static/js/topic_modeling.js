var topicModelingBERT = document.getElementById("topicModelingBERT");
    var splitToSentence = document.getElementById("splitToSentence");
    var topicModelingMALLET = document.getElementById("topicModelingMALLET");
    var optimizeTopicIntervals = document.getElementById("optimizeTopicIntervals");
    var topicModelingGensim = document.getElementById("topicModelingGensim");
    var removeStopwords = document.getElementById("removeStopwords");
    var lemmatizeWords = document.getElementById("lemmatizeWords");
    var nounsOnly = document.getElementById("nounsOnly");
    var topicCoherenceMALLET = document.getElementById("topicCoherenceMALLET");

    topicModelingBERT.addEventListener('change',function() {
        topicModelingMALLET.disabled = this.checked;
        optimizeTopicIntervals.disabled = this.checked;
        topicModelingGensim.disabled = this.checked;
        removeStopwords.disabled = this.checked;
        lemmatizeWords.disabled = this.checked;
        nounsOnly.disabled = this.checked;
        topicCoherenceMALLET.disabled = this.checked;

        if(this.checked){
            topicModelingMALLET.checked = false;
            optimizeTopicIntervals.checked = false;
            topicModelingGensim.checked = false;
            removeStopwords.checked = false;
            lemmatizeWords.checked = false;
            nounsOnly.checked = false;
            topicCoherenceMALLET.checked = false;
        }
    });

    topicModelingMALLET.addEventListener('change',function() {
        topicModelingBERT.disabled = this.checked;
        topicModelingGensim.disabled = this.checked;
        removeStopwords.disabled = this.checked;
        lemmatizeWords.disabled = this.checked;
        nounsOnly.disabled = this.checked;
        topicCoherenceMALLET.disabled = this.checked;

        if(this.checked){
            topicModelingGensim.checked = false;
            topicModelingGensim.checked = false;
            removeStopwords.checked = false;
            lemmatizeWords.checked = false;
            nounsOnly.checked = false;
            topicCoherenceMALLET.checked = false;
        }
    });

    topicModelingGensim.addEventListener('change',function() {
        topicModelingBERT.disabled = this.checked;
        topicModelingMALLET.disabled = this.checked;
        optimizeTopicIntervals.disabled = this.checked;
        
        if(this.checked){
            topicModelingBERT.checked = false;
            topicModelingMALLET.checked = false;
            optimizeTopicIntervals.checked = false;
            
        }
    });

    


    // 
    // 1. Check if directory is empty(data in directory)  
    // 2. Group !Bert  || !Mallet || !Gensim && Directory is empty or not) 
    // 3. Alert message and then 