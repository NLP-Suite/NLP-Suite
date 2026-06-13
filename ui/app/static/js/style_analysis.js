function toggleAnalysisDropdown() {
    const checkbox = document.getElementById('complexity_analysis');
    const dropdown = document.getElementById('analysis_dropdown');
    dropdown.disabled = !checkbox.checked;
}

  const minRatSlider = document.getElementById('min_rating');
  const minRatValue = document.getElementById('minRatingValue');
  const maxRatSlider = document.getElementById('max_rating_sd');
  const maxRatValue = document.getElementById('maxRatingSDValue');

  minRatSlider.addEventListener('input',function(){
    minRatValue.textContent = this.value;
  });
  maxRatSlider.addEventListener('input', function(){
    maxRatValue.textContent = this.value;
  });

function toggleRatingSliders() {
    const vocOptions = document.getElementById('voc_options').value;
    const isEnabled = vocOptions === '*' || vocOptions === 'Iconic';

    document.getElementById('min_rating').disabled = !isEnabled;
    document.getElementById('max_rating_sd').disabled = !isEnabled;
} 

function showGenderGuesserWarning() {
    const message = "Warning:\n\nWhen the Gender Guesser (Hacker Factor) webpage opens, make sure to read carefully the page content in order to understand:\n" +
                    "1. how this sophisticated neural network Java tool can guess the gender identity of a text writer (male or female);\n" +
                    "2. the difference between formal and informal text genre;\n" +
                    "3. the meaning of the gender estimate as 'Weak emphasis could indicate European';\n" +
                    "4. the limits of the algorithms (about 60-70% accuracy).\n\n" +
                    "You can also read Argamon, Shlomo, Moshe Koppel, Jonathan Fine, and Anat Rachel Shimoni. 2003. 'Gender, Genre, and Writing Style in Formal Written Texts,' Text, Vol. 23, No. 3, pp. 321–346.";
    const isConfirmed = confirm(message + "\n\nDo you want to keep the Gender Guesser option checked?");
    document.getElementById("gender_guesser").checked = isConfirmed;
}

toggleRatingSliders();
document.getElementById('complexity_analysis').addEventListener('change', toggleAnalysisDropdown);
toggleAnalysisDropdown(); 

// functions for dropdowns
function resetAll(){
    // document.getElementById("style-analysis").disabled = false;
    document.getElementById("complexity_analysis").disabled = false;
    document.getElementById("vocabulary_analysis").disabled = false;

    document.getElementById("tools").disabled = true;
    document.getElementById("analysis_dropdown").disabled = true;
    document.getElementById("voc_options").disabled = true;

}

// function toggleStyle(){

//     // const style = document.getElementById("style-analysis");
//     const complexity = document.getElementById("complexity_analysis");
//     const vocabulary = document.getElementById("vocabulary_analysis");
//     const tools = document.getElementById("tools");

//     if(style.checked){
//         complexity.disabled=true;
//         vocabulary.disabled=true;
        
//         tools.disabled=false;
//     }else{
//         resetAll();
//     }
// }
function toggleComplexity(){
    // const style = document.getElementById("style-analysis");
    const complexity = document.getElementById("complexity_analysis");
    const vocabulary = document.getElementById("vocabulary_analysis");

    const analysis = document.getElementById("analysis_dropdown");

    if(complexity.checked){
        // style.disabled=true;
        vocabulary.disabled=true;
        
        analysis.disabled=false;
    }else{
        resetAll();
    }
}
function toggleVocabulary(){
    // const style = document.getElementById("style-analysis");
    const complexity = document.getElementById("complexity_analysis");
    const vocabulary = document.getElementById("vocabulary_analysis");

    const voc = document.getElementById("voc_options");

    if(vocabulary.checked){
        complexity.disabled=true;
        // style.disabled=true;
        
        voc.disabled=false;
    }else{
        resetAll();
    }
}
// document.getElementById("style-analysis").addEventListener("change", toggleStyle);
document.getElementById("complexity_analysis").addEventListener("change", toggleComplexity);
document.getElementById("vocabulary_analysis").addEventListener("change", toggleVocabulary);
