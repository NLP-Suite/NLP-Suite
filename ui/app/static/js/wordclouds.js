function toggleForService(){
    var worldCloudService = document.getElementById("wordcloud_service");
    var numberOfWords = document.getElementById("maxNumberOfWords");
    var horizontalButton = document.getElementById("horizontal");
    // image-mask options are permanently disabled (coming soon) and not toggled here

    //gonna loop through this cause theres so many
    var listofElements = ['stopwords', 'lemmas', 'punctuation', 'lowercase_checkbox', 'collocation', 'differentColorsByPOS'];
    for(var i = 0; i < listofElements.length; i++){
        var id = listofElements[i];
        var checkbox = document.getElementById(id);
        if(worldCloudService.value !== "Python WordCloud"){
            checkbox.disabled = true;
        }
        else{
            checkbox.disabled = false;
        }
    }
    
    if(worldCloudService.value !== "Python WordCloud"){
        numberOfWords.disabled = true;
        horizontalButton.disabled = true;
    }
    else{
        numberOfWords.disabled = false;
        horizontalButton.disabled = false;
    }
}
document.getElementById("wordcloud_service").addEventListener("change", toggleForService);
toggleForService();