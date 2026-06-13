var extractLocations = document.getElementById("extractLocations");
        var columnLocationName = document.getElementById("columnLocationName");
        var geocodeLocations = document.getElementById("geocodeLocations");
        var geocoderSelect = document.getElementById("geocoderSelect");
        var area = document.getElementById("area");
        var restrict = document.getElementById("restrict");
        var mapLocations = document.getElementById("mapLocations");
        var mapLocationsSoftware = document.getElementById("mapLocationsSoftware");
        var viewGoogleApi = document.getElementById("viewGoogleApi");
        var boxforGoogle = document.getElementById("earthPro");

        geocodeLocations.addEventListener('change',function() {
            mapLocations.disabled = !this.checked;
            if(!this.checked){
                mapLocations.checked = false;
            }
        });


        geocoderSelect.addEventListener('change',function(){
            const selected = this.value;

            if(selected != "nominatim"){
                area.disabled = true;
                restrict.disabled = true;
            } else {
                area.disabled = false;
                restrict.disabled = false;
            }
        });
        
        //this disabled the options from map locations - can comment out if not needed
        mapLocations.addEventListener('change', function(){
            mapLocationsSoftware.disabled = !this.checked;
            boxforGoogle.disabled = !this.checked;
            if(!this.checked){
                mapLocationsSoftware.checked = false;
                boxforGoogle.disabled = true;
            }
        });
        
