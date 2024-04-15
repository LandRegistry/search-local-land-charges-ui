import $ from "jquery";

function downloadEvents(download_type){
    gtag('event', 'Download button click', {'eventCategory': 'Button click', 'eventLabel': download_type + ' download'})
}

$(document).ready(function() {
    $('#csv-download-link').click(function() {
        downloadEvents('csv');
    })

    $('#json-download-link').click(function() {
        downloadEvents('json');
    })

    $('#pdf-download-link').click(function() {
        downloadEvents('pdf');
    })

    $('#xml-download-link').click(function() {
        downloadEvents('xml');
    })
});
