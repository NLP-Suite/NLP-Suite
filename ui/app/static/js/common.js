function listofitems2(){

    var optionsSelect = document.getElementById("ngrams_options_list");
    var pickedSelect = document.getElementById("options");
    var plusbutton = document.getElementsByName("options-+")[0];
    var resetbutton = document.getElementsByName("options-reset")[0];
    var minusbutton = document.getElementsByName("options-show")[0];

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

listofitems2()


function submitbutton() {
  var sel1 = document.getElementById("options");
  var sel2 = document.getElementById("optionss");

  var out1 = "[";
  for (var i = 0; i < sel1.options.length; i++) {
    out1 = out1 + '"' + sel1.options[i].value + '"';
    if (i < sel1.options.length - 1) out1 = out1 + ",";
  }
  out1 = out1 + "]";

  var out2 = "[";
  for (var j = 0; j < sel2.options.length; j++) {
    out2 = out2 + '"' + sel2.options[j].value + '"';
    if (j < sel2.options.length - 1) out2 = out2 + ",";
  }
  out2 = out2 + "]";

  document.getElementById("ngrams_options_list_hidden").value = out1;
  document.getElementById("viewer_options_list_hidden").value = out2;

  return true;
}

