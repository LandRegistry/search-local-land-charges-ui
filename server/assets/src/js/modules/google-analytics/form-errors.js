const formErrorDataElement = document.getElementById('form-error-data');

// Only carry on if we have found a script block containing the form error json
if (formErrorDataElement) {
  const formErrorData = JSON.parse(formErrorDataElement.innerHTML);
  const formName = formErrorDataElement.getAttribute('data-form-name');

  formErrorData.forEach((item) => {
    // eslint-disable-next-line no-unused-vars
    item.errors.forEach((error) => {
      window.gtag('event', `${formName} : ${item.name}`, {
        event_category: 'FormValidation',
        // Sending the actual error in the event label is commented out by default
        // If you wish to send error messages to google analytics, you can comment out the following line
        // However, if doing this, you must be aware that if your error messages contain any
        // sensitive information such as email addresses, that this would be a problem from a
        // GDPR and general privacy perspective, as well as potentially leaking other data to google.
        //
        // This might occur if you were to replay user input back to people in the error message, such as:
        // "john.smith@example.com is not a valid email address"
        //
        // If you are confident that this is not the case, and will never be the case with your errors,
        // then you may uncomment this line.
        //
        // 🐉🐉 HERE BE DRAGONS! 🐉🐉
        // 'event_label': error
      });
    });
  });
}
