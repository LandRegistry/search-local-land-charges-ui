import $ from "jquery";
import accessibleAutocomplete from 'accessible-autocomplete'

let getRequestedOption = function(element, text) {
  return Array.prototype.filter.call(element.options, option => (option.textContent || option.innerText) === text)[0];
}

let addOption = function(element, text) {
  for (let alreadyAdded of element.querySelectorAll('option[data-added-option^="yes"]')) {
    alreadyAdded.remove();
  }
  let option = document.createElement("option");
  option.text = text;
  option.value = text;
  option.setAttribute("data-added-option", "yes");
  element.add(option);
  return option;
}

let duplicateLabel = function(element) {
  let copyLabel = document.querySelector('label[for^="' + element.name + '"');
  let newLabel = copyLabel.cloneNode(true);
  newLabel.setAttribute('for', copyLabel.getAttribute('for') + '-select');
  newLabel.classList.add('govuk-visually-hidden');
  copyLabel.after(newLabel);
}

let selectorsForAutocomplete = document.querySelectorAll('select[data-use-autocomplete^="yes"]');

for (let selectAutocomplete of selectorsForAutocomplete) {
  //Create additional hidden label for renamed select to pass accessibility check
  duplicateLabel(selectAutocomplete);
  accessibleAutocomplete.enhanceSelectElement({
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
    $(inputElement).trigger("focus");
    $(inputElement).trigger("blur");
  });
  $(inputElement).on("keypress", function(event) {
    if (event.which == 13) {
      this.trigger("blur");
    }
  });
  // More hacks to allow blank looking input while passing html validation
  if ($(inputElement).val() == '\xa0') {
    $(inputElement).val("");
  }
}
