from datetime import datetime
from urllib.parse import urlparse
from flask import Blueprint, flash, make_response, redirect, render_template, request, url_for, g
from server.services.back_link_history import get_back_url
from server.services.datetime_formatter import format_date
from server import config
from server.utils.base64_cookie import check_valid_base64_json_cookie, encode_base64_json_cookie
from server.views.forms.cookies_form import CookiesForm
from server.services.datetime_formatter import format_long_date
from dateutil.parser import parse
from flask_babel import gettext as _

# This is the blueprint for the default privacy, accessibility and cookies pages.
# Do not add your own service routes to this blueprint.
main = Blueprint("main", __name__, template_folder="../templates/main")


@main.route("/accessibility-statement")
def accessibility_statement():
    accessibility_publish = format_date(datetime.strptime(
        config.ACCESSIBILITY_STATEMENT_PUBLISH, '%d/%m/%Y').date())
    accessibility_update = format_date(datetime.strptime(
        config.ACCESSIBILITY_STATEMENT_UPDATE, '%d/%m/%Y').date())

    return render_template('accessibility-statement.html', accessibility_publish=accessibility_publish,
                           accessibility_update=accessibility_update)


@main.route("/cookies", methods=["GET", "POST"])
def cookies_page():
    form = CookiesForm()
    # Default cookies policy to reject all categories of cookie
    cookies_policy = {"analytics": "no"}

    if form.validate_on_submit():
        # Update cookies policy consent from form data
        cookies_policy["analytics"] = form.analytics.data

        # Create flash message confirmation before rendering template
        flash(
            f'<p class="govuk-notification-banner__heading">{_("You’ve set your cookie preferences. ")}'
            f'<a class="govuk-notification-banner__link" href="{url_for("index.index_page")}">'
            f'{_("Go back to the page you were looking at")}</a>.</p>', "success")

        # Create the response so we can set the cookie before returning
        response = make_response(render_template("cookies.html", form=form))

        # If cookies have been declined, remove any existing ones from previous acceptances
        if form.analytics.data == "no":
            cookie_names = [cookie_name for cookie_name in request.cookies.keys() if cookie_name.startswith("_g")]
            for cookie_name in cookie_names:
                response.delete_cookie(cookie_name, path='/', domain=_get_dot_preceded_domain())

        # Set cookies policy for one year
        response.set_cookie(
            "cookies_policy",
            encode_base64_json_cookie(cookies_policy),
            max_age=31557600,
            samesite="Lax",
        )
        return response
    elif request.method == "GET":
        if request.cookies.get("cookies_policy"):
            # Set cookie consent radios to current consent
            cookie_valid, cookie_json = check_valid_base64_json_cookie(request.cookies.get("cookies_policy"))
            if cookie_valid:
                form.analytics.data = cookie_json["analytics"]
            else:
                form.analytics.data = cookies_policy["analytics"]
        else:
            # If consent not previously set, use default "no" policy
            form.analytics.data = cookies_policy["analytics"]
    return render_template("cookies.html", form=form)


@main.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("terms-and-conditions.html")


@main.route("/back")
def back():
    return redirect(get_back_url())


@main.route('/release-notices')
def release_notices():
    release_notice_url = config.RELEASE_NOTICES_URL
    if release_notice_url == 'TEST':
        release_notices = get_test_data()
    else:
        release_notices = g.requests.get(release_notice_url).json()

    release_notices.sort(key=lambda release_notice: parse(release_notice['name']), reverse=True)

    if g.locale == 'cy':
        for release_notice in release_notices:
            release_notice['name'] = format_long_date(release_notice['name'])

    return render_template('release-notices.html',
                           release_notices=release_notices)


@main.route('/how-to-use-the-map')
def map_help():
    return render_template('map-help.html')


def get_test_data():
    return [{"name": "22nd January 2023", "link": "https://google.com"},
            {"name": "10th May 2023", "link": "https://google.com"},
            {"name": "1st January 2020", "link": "https://google.com"},
            {"name": "2nd June 2021", "link": "https://google.com"},
            {"name": "3rd July 2022", "link": "https://google.com"},
            {"name": "11th November 2019", "link": "https://google.com"},
            {"name": "5th September 2022", "link": "https://google.com"}]


def _get_dot_preceded_domain() -> str:
    domain: str = urlparse(request.base_url).hostname
    return None if domain == "localhost" else f".{domain}"
