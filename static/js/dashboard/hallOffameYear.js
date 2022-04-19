$(document).ready(function () {

  var imgId = $(".halloffame").find("img").attr("su-media-id")

  $("#confirmyear").click(function () {
    console.log("Meloo");
    $.ajax({
      type: "POST",
      url: "/dashboard/hallOffameYear",
      data: {imgId:imgId},
      success: function () {
        console.log("ana chahiye")
        window.location = "/Artwork-of-the-year";
      },
    });
  });
});