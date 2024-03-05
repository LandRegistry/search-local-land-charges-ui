function nonMigratedButtonClick(button){
    gtag('event', button + ' button clicked', {'eventCategory': 'Non migrated page'});
}


$(document).ready(function() {
    $('#non-migrated-start-new').click(function() {
        nonMigratedButtonClick("Start new");
    })

    $('#non-migrated-edit').click(function() {
        nonMigratedButtonClick("Edit");
    })
});
