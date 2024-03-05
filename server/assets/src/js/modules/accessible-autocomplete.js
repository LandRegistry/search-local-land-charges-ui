import accessibleAutocomplete from 'accessible-autocomplete'

let getRequestedOption = function(element, text) {
  return Array.prototype.filter.call(element.options, option => (option.textContent || option.innerText) === text)[0];
}

let addOption = function(element, text) {
  let option = document.createElement("option");
  option.text = text;
  element.add(option);
  return option;
}

let selectorsForAutocomplete = document.querySelectorAll('select[data-use-autocomplete^="yes"]');

for (let selectAutocomplete of selectorsForAutocomplete) {
  accessibleAutocomplete.enhanceSelectElement({
    name: "accessible-autocomplete",
    selectElement: selectAutocomplete,
    defaultValue: selectAutocomplete.getAttribute("data-default-value") || undefined,
    displayMenu: "overlay",
    tNoResults: function() {
      return _('No results found');
    },
    onConfirm: function(query) {
      let requestedOption = getRequestedOption(this.selectElement, query);
      if (!requestedOption) {
        let inputField = this.element.querySelector('input#' + this.id);
        requestedOption = getRequestedOption(this.selectElement, inputField.value);
        // If still not a requestedOption then add text as an option
        if (!requestedOption && inputField.value != '') {
          requestedOption = addOption(this.selectElement, inputField.value);
        }
      }
      if (requestedOption) { requestedOption.selected = true }
      else { selectAutocomplete.selectedIndex = -1 }
    }
  });
  let requestedOption = getRequestedOption(selectAutocomplete, selectAutocomplete.getAttribute("data-default-value"));
  if (!requestedOption && selectAutocomplete.getAttribute("data-default-value") != '') {
    $('input#' + selectAutocomplete.name).value = selectAutocomplete.getAttribute("data-default-value");
  }
  // Slight hack to trigger onConfirm
  let inputElement = $('input#' + selectAutocomplete.name)[0]
  let inputForm = $(inputElement.form)[0]
  $(inputForm).on("submit", function() {
    $(inputElement).focus();
    $(inputElement).blur();
  });
  $(inputElement).on("keypress", function(event) {
    if (event.which == 13) {
      this.blur();
    }
  });
}
