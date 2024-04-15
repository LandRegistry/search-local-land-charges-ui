import $ from "jquery";

$(function() {
    $('video[data-ga-video-play^="yes"').on("play", function(event) {
        gtag('event', event.target.id + " video played", {'eventCategory': 'Video play'});
    });
});
