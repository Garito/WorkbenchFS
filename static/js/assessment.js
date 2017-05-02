function toggleQRCodeReader(e) {
  var group = $(e.target).parents(".form-group"), camera = group.siblings(".camera");

  if(camera.length) {
    camera.html5_qrcode_stop().remove();
  } else {
    var camera = $('<div class="camera" style="min-height: 300px;"></div>');
    group.after(camera);
    camera.html5_qrcode(function(data) {
      var parts = data.split("/");
      group.find("input").val(parts[parts.length - 1]);
    }, function(error){
      console.log(error);
    }, function(videoError) {
      console.log(videoError);
    });
  }
}

$(document).ready(function() {
  $(".qrcode").on("click", toggleQRCodeReader);
});