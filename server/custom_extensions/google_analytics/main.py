from flask import request

from server import config
from server.utils.base64_cookie import check_valid_base64_json_cookie


class GoogleAnalytics(object):
    """Add Google Analytics support to apps. Including form validation events"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        app.config.setdefault("GOOGLE_ANALYTICS_KEY", False)

        @app.context_processor
        def inject_global_values():
            # Exclude GA key (and thus prevent GA running) if policy not set to yes
            cookies_policy = request.cookies.get('cookies_policy')
            if cookies_policy:
                cookie_valid, cookie_json = check_valid_base64_json_cookie(cookies_policy)
                if cookie_valid and cookie_json.get('analytics') == "yes":
                    return dict(google_analytics_key=config.GOOGLE_ANALYTICS_KEY)
                else:
                    return dict(google_analytics_key=False)
            return dict(google_analytics_key=False)

        app.jinja_env.filters["build_form_errors"] = build_form_errors


def build_form_errors(data):
    """Build form errors

    Recursive method to take wtforms' error structure and flatten it out.
    This turns the nested structure (if you have nested sub-forms) into
    a simpler list of form element names and associated errors, ready for
    sending to Google Analytics
    """
    ret = []

    for key, value in data.items():
        if isinstance(value, (list,)):
            ret.append({"name": key, "errors": value})
        else:
            sub_data = build_form_errors(value)

            for item in sub_data:
                ret.append(
                    {
                        "name": "{}-{}".format(key, item["name"]),
                        "errors": item["errors"],
                    }
                )

    return ret
