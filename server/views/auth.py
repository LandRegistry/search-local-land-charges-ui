import base64
from dataclasses import make_dataclass
from functools import wraps

from flask import Blueprint, current_app, g, redirect, request, session, url_for
from jwt_validation.validate import validate

from server import config
from server.main import app

auth = Blueprint("auth", __name__)


def authenticated(f):
    """Decorator for use on Flask routes that should only be accessible to users that are logged in"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            redirect_uri = url_for("auth.login")
            if "/" != request.path:
                # User not logged in. Redirect to the login page adding the intended destination as a query parameter
                redirect_uri = url_for(
                    "auth.login",
                    requestedpath=base64.urlsafe_b64encode((request.full_path).encode("utf-8")),
                    _external=True,
                )
            return redirect(redirect_uri)

        return f(*args, **kwargs)

    return decorated


@auth.route("/login")
def login():
    """Redirects to the login page. Redirects to the authorised route upon successful login."""
    current_app.logger.info("login")
    redirect_uri = url_for("auth.authorized", _external=True)
    if "requestedpath" in request.args:
        # Preserve the destination that was attempted before redirection to the login page
        requested_path = request.args["requestedpath"]
        redirect_uri = url_for("auth.authorized", requestedpath=requested_path, _external=True)

    current_app.logger.info("redirect_url: %s", redirect_uri)

    return redirect(url_for("sign_in.handle_sign_in", redirect_uri=redirect_uri))


@auth.route("/logout")
def logout():
    """logs the user out."""
    session.clear()

    return redirect(url_for("index.index_page", _external=True))


@auth.route("/authorized")
def authorized():
    if "requestedpath" in request.args:
        # Redirect the user to the page they attempted to access before being redirected to the login page
        requested_path = request.args["requestedpath"]
        decoded_data = base64.urlsafe_b64decode(requested_path.encode("utf-8"))
        requested_path = str(decoded_data, "utf-8")
        current_app.logger.info("authorize - requested_path: %s", requested_path)
        auth_response = redirect(requested_path)
    else:
        auth_response = redirect(url_for("search.search_by_post_code_address", _external=True))

    # Pull things we need from session because we're going to nuke it
    token = session["jwt_token"]
    zoom_to_authority = session.get("zoom_to_authority")
    # Clear the session and manually save so that it's removed from redis
    session.clear()
    app.session_interface.save_session(app, session, auth_response)
    # Manually create new session, use fake request and cookie so we create a new session ID
    fake_request = make_dataclass("FakeRequest", ["cookies"])
    fake_request.cookies = {}
    new_session = app.session_interface.open_session(app, fake_request)
    # Put login information into new session and save it
    userinfo = validate(f"{config.AUTHENTICATION_URL}/v2.0/authentication/validate", token, g.requests)
    new_session["jwt_payload"] = userinfo
    new_session["profile"] = {
        "user_id": userinfo.sub,
        "name": f"{userinfo.principle.first_name} {userinfo.principle.surname}",
    }
    new_session["zoom_to_authority"] = zoom_to_authority
    new_session["jwt_token"] = token
    app.session_interface.save_session(app, new_session, auth_response)
    # Set session to not modified so session handling doesn't mess with the session cookie we just set up
    session.modified = False

    return auth_response
