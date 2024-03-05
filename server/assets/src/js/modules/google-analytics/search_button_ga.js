$(document).ready(function() {
    $("#search-form").submit(function(event) {
        gtag(event, 'Search button clicked', {'eventCategory': 'Search page'})
    });
});
