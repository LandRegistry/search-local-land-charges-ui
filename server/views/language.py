from datetime import datetime, timedelta
from flask import Blueprint, redirect, url_for, make_response, request

from server import config

# This is the blueprint object that gets registered into the app in blueprints.py.
language = Blueprint("language", __name__, url_prefix="/language")


@language.route('<any("en", "cy"):language>')
def change_language(language):
    # Just so locally we don't end up on the english home page when switching to welsh and visa versa
    if request.referrer.endswith(config.HOME_PAGE_CY_URL) or \
            request.referrer.endswith(config.HOME_PAGE_EN_URL):
        response = make_response(redirect(url_for('index.index_page')))
    else:
        response = make_response(redirect(request.referrer))

    return set_language_cookie(response, language)


def set_language_cookie(response, language):
    cookie_expiry_date = datetime.now() + timedelta(days=365)
    response.set_cookie('language', value=language, expires=cookie_expiry_date, httponly=True)
    return response
