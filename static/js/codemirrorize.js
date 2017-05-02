function codemirrorize(elem, readonly) {
  var $this = $(elem), $code = $this.html(), $unescaped = $("<div/>").html($code).text();
  $this.empty();
  var settings = {value: $unescaped, lineNumbers: true, viewportMargin: Infinity};
  if(typeof readonly === "undefined" || readonly == true) {
    settings["readOnly"] = "nocursor";
  }
  elem.codemirror = CodeMirror(elem, settings);
}

$(document).ready(function() {
  $(".codemirror").each(function() {
    codemirrorize(this);
  });
});