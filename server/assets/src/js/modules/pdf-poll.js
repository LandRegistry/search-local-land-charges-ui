import $ from "jquery";

var pdfPollElement = document.getElementById('pdf-poll-variables')
var pdfPollVariables = JSON.parse(pdfPollElement.innerHTML)

var csrf_token = pdfPollVariables['csrf_token'];
var pdf_poll_interval = pdfPollVariables['pdf_poll_interval'];
var pdf_poll_url = pdfPollVariables['pdf_poll_url'];
var pdf_poll_complete_url = pdfPollVariables['pdf_poll_complete_url'];
var pdf_poll_failure_url = pdfPollVariables['pdf_poll_failure_url'];

var pdf_interval = null;

var poll_for_pdf = function(pdf_poll_url, pdf_poll_complete_url, pdf_poll_interval) {
    pdf_interval = setInterval(poll_pdf, pdf_poll_interval, pdf_poll_url, pdf_poll_complete_url);
};

function poll_pdf(pdf_poll_url, pdf_poll_complete_url) {
    $.ajax({
        type: 'GET',
        url: pdf_poll_url,
        complete: function(jqXHR, textStatus) {
            if (jqXHR.status === 201){
                clearInterval(pdf_interval);
                $(location).attr('href', pdf_poll_complete_url);
            } else if (jqXHR.status != 202){
                $(location).attr('href', pdf_poll_failure_url)
            }
        }
    });
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }
});

$(document).ready(function(){
    poll_for_pdf(pdf_poll_url, pdf_poll_complete_url, pdf_poll_interval);
});
