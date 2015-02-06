var main = function(){
$("#signup").click(function () {
   $('.nav').slideUp(50);
    $(".nav1").show(800);
});

$("#back").click(function () {
   $('.nav1').slideUp(50);
    $(".nav").show(800);
});

};

$(document).ready(main);

