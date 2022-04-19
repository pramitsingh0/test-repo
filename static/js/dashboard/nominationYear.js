$(document).ready(function () {
  var selectedImg = [];

  $(".image-checkbox").on("click", function (e) {
    var selected = {
      id: $(this).find("img").attr("su-media-id"),
      src: $(this).find("img").attr("src"),
    };
    $(".image-checkbox-checked").each(function () {
      $(this).removeClass("image-checkbox-checked");
    });
    selectedImg = [];
    selectedImg.push(selected);
    $(this).addClass('image-checkbox-checked');
    console.log(selectedImg[0]["id"]);
  });


  $("#best-artwork-add").click(function () {
    var month = $("#month").val();
    $.ajax({
      type: "POST",
      url: "/dashboard/nominationYear",
      contentType: "application/json",
      data: JSON.stringify({ imgArray: selectedImg, month: month }),
      success: function () {
        window.location = "/dashboard/hallOffameYear?id="+selectedImg[0]["id"]+'&image='+selectedImg[0]["src"];
      },
    });
  });
});
