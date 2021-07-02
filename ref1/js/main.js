$(document).ready(function() {
    $(".kal_cont").each(function(i){ 
        $(this).mousemove(function(e) {
            $(this).find(".ksc").each(function(i){ 
                $(this).css({backgroundPosition: e.pageX+"px "+e.pageY+"px"});
            });
        });
    });
});