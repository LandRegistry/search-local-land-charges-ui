import $ from "jquery";

$(".stop-click-propagation").on("click", function(e) {
    e.stopPropagation();
});
