import $ from "jquery";

$('a[data-s3-redirect="yes"]').on("click", function(e) {
    let linkUrl = $(this).attr("href");
    $.ajax({
        type: 'GET',
        url: linkUrl,
        complete: function(jqXHR, textStatus) {
            if (jqXHR.status === 200){
                $(location).attr('href', jqXHR.responseText);
            } else {
                $(location).attr('href', linkUrl + "/error")
            }
        }
    });
    e.preventDefault();
});
