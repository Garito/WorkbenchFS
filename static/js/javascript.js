function convertTimes() {
  moment.locale(navigator.language || navigator.userLanguage);

  $("time").each(function() {
    var $this = $(this);
    if($this.parent().hasClass("date")) {
      $this.html(moment($this.attr("datetime")).format("LL"));
    } else {
      $this.html(moment($this.attr("datetime")).format("HH:mm:ss"));
    }
  });
}

$(document).ready(function() {
  convertTimes();
});