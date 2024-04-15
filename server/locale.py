from flask import request


def get_locale():
    if "language" in request.cookies:
        return request.cookies.get("language")
    else:
        return "en"
