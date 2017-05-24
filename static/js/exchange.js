function update(e) {
  var btn = $(e.target), icon = btn.find("i");
  icon.removeClass("fa-download").addClass("fa-spinner fa-spin");
  $.getJSON("/pullRemoteGit").done(function(data) {
    console.log(data);
  }).fail(function(jqxhr, textStatus, error) {

  }).always(function() {
    icon.removeClass("fa-spinner fa-spin").addClass("fa-download");
    btn.addClass("disabled");
  });
}

$(document).ready(function() {
  $("button.update").on("click", update)
});