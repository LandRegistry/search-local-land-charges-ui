// Dont display if cookies banner not present
if (document.getElementById('cookie-banner')) {
  const cookieBanner = document.getElementById('cookie-banner');
  const defaultMessage = document.getElementById('default-message');
  const acceptedMessage = document.getElementById('accepted-message');
  const rejectedMessage = document.getElementById('rejected-message');

  // Accept additional cookies
  document
    .getElementById('accept-cookies')
    .addEventListener('click', function () {
      // If only using one category of cookie, ammend the policy content as appropriate
      document.cookie =
        'cookies_policy=' + window.btoa('{"analytics": "yes"}') + '; max-age=31557600; path=/; secure; samesite=lax';
      defaultMessage.hidden = true;
      acceptedMessage.hidden = false;
    });

  // Reject additional cookies
  document
    .getElementById('reject-cookies')
    .addEventListener('click', function () {
      // If only using one category of cookie, ammend the policy content as appropriate
      document.cookie =
        'cookies_policy=' + window.btoa('{"analytics": "yes"}') + '; max-age=31557600; path=/; secure; samesite=lax';
      defaultMessage.hidden = true;
      rejectedMessage.hidden = false;
    });

  // Hide accepted message
  document
    .getElementById('accepted-hide')
    .addEventListener('click', function () {
      acceptedMessage.hidden = true;
      cookieBanner.hidden = true;
    });

  // Hide rejected message
  document
    .getElementById('rejected-hide')
    .addEventListener('click', function () {
      rejectedMessage.hidden = true;
      cookieBanner.hidden = true;
    });
}
