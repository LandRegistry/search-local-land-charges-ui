import $ from "jquery";

function sendPageviewOnSubmit(submitButtonId) {
    document.getElementById(submitButtonId).disabled = true
    gtag('event', 'Continue button clicked', {'eventCategory': '/payment'})
    return true
}

$(document).ready(function() {
    $('#confirm-address-form').submit(function() {
        sendPageviewOnSubmit('submit');
    })

    $('#search-area-description-form').submit(function() {
        sendPageviewOnSubmit('submit');
    })
});
