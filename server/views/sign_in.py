from flask import render_template, request, redirect, url_for, session, current_app, g, Blueprint, make_response, \
    flash
from flask_babel import force_locale, lazy_gettext as _
from server import config

from server.dependencies.audit_api.audit_api_service import AuditAPIService
from server.dependencies.authentication_api import AuthenticationApi
from server.dependencies.search_local_land_charge_api.search_local_land_charge_service \
    import SearchLocalLandChargeService

from server.views.forms.sign_in_form import SignInForm
from server.views.language import set_language_cookie
from jwt_validation.validate import validate

sign_in = Blueprint("sign_in", __name__, template_folder="../templates/sign-in")


@sign_in.route("/sign-in", methods=["GET", "POST"])
def handle_sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        current_app.logger.info("Valid sign-in form, checking user")
        check_result = check_user(form)
        if check_result:
            return check_result

    redirect_uri = request.args.get('redirect_uri', form.redirect_uri.data)
    # if already signed in, direct to map page, if no redirect_url go to login, otherwise go to sign-in page
    if "profile" in session and "user_id" in session['profile']:
        return redirect(url_for('search.search_by_post_code_address'))
    elif not redirect_uri:
        return redirect(url_for("auth.login"))
    else:
        service_messages = SearchLocalLandChargeService(current_app.config).get_service_messages()
        if service_messages:
            flash(service_messages, "service_message")
        from_homepage = False
        if request.referrer and request.referrer.endswith(current_app.config['HOME_PAGE_CY_URL']):
            g.locale = "cy"
            from_homepage = True
        elif request.referrer and request.referrer.endswith(current_app.config['HOME_PAGE_EN_URL']):
            g.locale = "en"
            from_homepage = True
        if from_homepage:
            g.requests.headers.update({'Locale': g.locale})
            with force_locale(g.locale):
                response = make_response(
                    render_template('sign-in.html',
                                    form=form,
                                    redirect_uri=redirect_uri))
                return set_language_cookie(response, g.locale)
        else:
            return render_template('sign-in.html',
                                   form=form,
                                   redirect_uri=redirect_uri)


def check_user(form):
    success, result = AuthenticationApi().authenticate(form.username_password.password.data,
                                                       form.username_password.username.data)
    if success:
        userinfo = validate(f"{config.AUTHENTICATION_URL}/v2.0/authentication/validate", result, g.requests)
        if userinfo.principle.status == "Invited":
            session["registered_email"] = userinfo.principle.email
            return redirect(url_for("account_admin.resend_activation_email"))
        session['jwt_token'] = result
        return redirect(form.redirect_uri.data)
    if result.get('locked', False):
        message = _('You tried to log in using an invalid username or password. For security reasons, '
                    'your account status has been changed to inactive')
        form.username_password.errors = {'username_password': [message]}
        current_app.logger.warn(f"User account {form.username_password.username.data} locked")
        AuditAPIService.audit_event('User authentication failed x10 - account locked',
                                    supporting_info=result)
    else:
        form.username_password.errors = {
            'username_password': [_('Email address and password do not match, try again or reset your password')]}

    return None
