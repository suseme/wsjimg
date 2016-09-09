( function( $ ) {
  $('.swipebox').swipebox();
} )( jQuery );

var loadImgs = function(jsonPath) {
  $.getJSON(jsonPath, function(data){
    $("title").text(data["title"]);
    
    var imgHtml = "";
    $.each(data["imgs"], function(imgIndex, img){
      imgHtml += "<li><img src=\"$src$\" alt=\"$alt$\"/></li>".replace("$src$", img["src"]).replace("$alt$", img["alt"]);
    });
    
    $("#imgs").empty();
    $("#imgs").html(imgHtml);
  });
};

var temp = function(tempStr, tag, obj) {
  return tempStr.replace("$"+tag+"$", obj[tag])
}