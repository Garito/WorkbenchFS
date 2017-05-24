function togglePhase(e) {
  var toggler = $(e.target);
  if(toggler.prop("tagName") !== "TD") {
    toggler.children("i");
  } 

  toggler.parents("tr:first").find(".codemirror").toggleClass("hidden");
  toggler.toggleClass("fa-minus fa-plus");
}

$(document).ready(function() {
  $("table > tbody > tr:not(:last-child)").find(".codemirror").addClass("hidden");
  $("table .toggler").on("click", togglePhase)
});