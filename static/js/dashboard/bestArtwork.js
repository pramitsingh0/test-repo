$(document).ready(function () {
  var selectedImg = [];
  $(".image-checkbox").on("click", function (e) {
    var selected = {id:$(this).find("img").attr("su-media-id"), src:$(this).find("img").attr("src")};
    if ($(this).hasClass("image-checkbox-checked")) {
      $(this).removeClass("image-checkbox-checked");
      selectedImg = $.grep(selectedImg, function (value) {
        return value.id != selected.id;
      });
    } else {
      $(this).addClass("image-checkbox-checked");
      selectedImg.push(selected);
    }
  });
  $("#best-artwork-add").click(function () {
    var month = $("#month").val();
    $.ajax({
      type: "POST",
      url: "/dashboard/bestArtwork",
      contentType: 'application/json',
      data: JSON.stringify({imgArray: selectedImg, month: month}),

      success: function () {
        window.location = "/dashboard/nomination";
      },
    });
  });
});
