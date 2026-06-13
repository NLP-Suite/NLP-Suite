var coreferenceCheckbox = document.getElementById("coreferenceResolution");
        var manualCoreference = document.getElementById("manualCoreference");
        var svoPackage = document.getElementById("package");
        var lemmatizeSubjects = document.getElementById("lemmatize_subjects");
        var filterSubjects = document.getElementById("filter_subjects");
        var lemmatizeVerbs = document.getElementById("lemmatize_verbs");
        var filterVerbs = document.getElementById("filter_verbs");
        var lemmatizeObjects = document.getElementById("lemmatize_objects");
        var filterObjects = document.getElementById("filter_objects");
        var soGender = document.getElementById("so_gender");
        var soQuote = document.getElementById("so_quote");

        // coreferenceCheckbox.addEventListener('change',function() {
        //     manualCoreference.disabled = !this.checked;
        //     if(!this.checked){
        //         manualCoreference.checked = false;
        //     }
        // });
        lemmatizeSubjects.addEventListener('change',function() {
            filterSubjects.disabled = !this.checked;
            if(!this.checked){
                filterSubjects.checked = false;
            }
        });

        lemmatizeVerbs.addEventListener('change',function() {
            filterVerbs.disabled = !this.checked;
            if(!this.checked){
                filterVerbs.checked = false;
            }
        });

        lemmatizeObjects.addEventListener('change',function() {
            filterObjects.disabled = !this.checked;
            if(!this.checked){
                filterObjects.checked = false;
            }
        });

        svoPackage.addEventListener('change',function(){
            const selected = this.value;

            if(selected != "Stanford CoreNLP"){
                soGender.disabled = true;
                soQuote.disabled = true;
            } else {
                soGender.disabled = false;
                soQuote.disabled = false;
            }
        });
        