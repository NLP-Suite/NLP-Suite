function onlyone() {
  var buttons = document.getElementsByClassName("run-button");
  if (!buttons || buttons.length === 0){
    return
  }

  document.onchange = function (button) {
    if (button && button.target && button.target.type === "checkbox") {
      var count = 0;
      var inputs = document.getElementsByTagName("input");
      for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type === "checkbox" && !inputs[i].disabled && inputs[i].checked) {
          count++;
        }
      }
      for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = count === 0;
      }
    }
  };

  for (var i = 0; i < buttons.length; i++) {
    buttons[i].onclick = function (button) {
      var count = 0;
      var inputs = document.getElementsByTagName("input");
      for (var j = 0; j < inputs.length; j++) {
        if (inputs[j].type === "checkbox" && !inputs[j].disabled && inputs[j].checked) {
          count++;
        }
      }
      if (count === 0) {
        button.preventDefault();
        alert("Please select at least one option.");
      }
    };
  }
}

onlyone();