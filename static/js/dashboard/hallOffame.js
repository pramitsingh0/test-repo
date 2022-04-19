$(document).ready(function () {

  var imgId = $(".halloffame").find("img").attr("su-media-id")

  $("#confirm").click(function () {
    console.log("hello");
    $.ajax({
      type: "POST",
      url: "/dashboard/hallOffame",
      data: {imgId:imgId},
      success: function () {
        window.location = "/hall-of-fame";
      },
    });
  });
});