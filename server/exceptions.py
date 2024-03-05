from flask import jsonify, render_template
from jinja2 import TemplateNotFound

from server.utils.content_negotiation_utils import request_wants_json


def http_error_renderer(description, code, http_code, e=None):
    if request_wants_json():
        return jsonify({}), http_code
    else:
        return render_template("errors/unhandled.html", http_code=http_code), http_code


def unhandled_error_renderer(description, code, http_code, e=None):
    if request_wants_json():
        return jsonify({}), 500
    else:
        return render_template("errors/unhandled.html", http_code=http_code), http_code


def application_error_renderer(description, code, http_code, e=None):
    e = {"message": None, "code": None} if e is None else e

    if request_wants_json():
        return jsonify({"message": e.message, "code": e.code}), http_code
    else:
        try:
            return (
                render_template(
                    "errors/application/{}.html".format(e.code),
                    description=e.message,
                    code=e.code,
                    http_code=http_code,
                    e=e,
                ),
                http_code,
            )
        except TemplateNotFound:
            # Uncomment this to start showing application error messages
            # return (
            #     render_template(
            #         "errors/application.html",
            #         description=e.message,
            #         code=e.code,
            #         http_code=http_code,
            #     ),
            #     http_code,
            # )
            return render_template("errors/unhandled.html", http_code=http_code), http_code
