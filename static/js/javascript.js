function convertTimes() {
  moment.locale(navigator.language || navigator.userLanguage);

  $("time").each(function() {
    var $this = $(this);

    $this.html(moment($this.attr("datetime")).format("HH:mm:ss"));
  });
}

$(document).ready(function() {
  convertTimes();
});