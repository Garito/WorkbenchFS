var usbs = {}

function refresh_usbs(data) {
  $("td.usb > a").addClass("hidden");

  for(var key in data["usbs"]) {
    $("tr[computer=" + key + "] > td.usb > a").removeClass("hidden");
  }

  usbs = data["usbs"];
}

function add_new_invs(table, data) {
  table.children("tbody").prepend(data["inv"]["newInvs"]);
  var total_placeholder = $("h1 small"), total = parseInt(total_placeholder.text().replace("(", "").replace(")", ""));      
  total_placeholder.text("(" + (total + data["inv"]["total"]) + ")");

  for(var key in data["inv"]["newPhases"]) {
    $("tr#" + key).replaceWith(data["inv"]["newPhases"][key]);
  }

  convertTimes();

  table.attr("last", data["inv"]["last"]);
}

function checkNews() {
  var table = $("table"), last = table.attr("last");

  $.getJSON("/getNews", {"last": last}).done(function(data) {
    if(JSON.stringify(data["usbs"]) !== JSON.stringify(usbs)) {
      refresh_usbs(data)
    }

    if(data["inv"]) {
      add_new_invs(table, data)
    }
  });

  setTimeout(checkNews, 5000);
}

$(document).ready(function() {
  checkNews();
});