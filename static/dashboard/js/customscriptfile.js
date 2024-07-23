$(document).ready(function () {
    $(".sideMenuToggler").on("click", function () {
        $(".wrapper").toggleClass("active");
    });
});


/* // ***********Nav Tabs Switching to work proplorly************ */

$("ul.nav.nav-pills li.nav-item a").click(function () {
    $("ul.nav.nav-pills li.nav-item a.active").removeClass('active');
    $(this).addClass('active');
});




/* // *****************tooltip Initiating**************** */

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

window.setTimeout(function(){$(".loader").addClass("opacity_hide");}, 700);
window.setTimeout(function(){$(".wrapper").addClass("opacity_show");}, 300);