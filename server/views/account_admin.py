from flask import flash, redirect, render_template, current_app, Blueprint, session, url_for
from server.dependencies.account_api.account_api_service import AccountApiService
from server.dependencies.audit_api.audit_api_service import AuditAPIService
from server.services.paid_search_utils import PaidSearchUtils
from server.views.forms.change_password_with_token_form import ChangePasswordWithTokenForm
from server.views.forms.expired_activation_form import ExpiredActivationForm
from server.views.forms.register_form import RegisterForm
from landregistry.exceptions import ApplicationError
from flask_babel import lazy_gettext as _
from server.views.forms.reset_password_form import ResetPasswordForm

account_admin = Blueprint("account_admin", __name__, template_folder="../templates/account-admin")
account_admin.add_app_template_filter(PaidSearchUtils.format_search_id, "format_search_id")


@account_admin.route("/register", methods=["GET", "POST"])
def register():
    current_app.logger.info("Register page")

    form = RegisterForm()

    if form.validate_on_submit():
        current_app.logger.info("Valid registration form")

        account_service = AccountApiService(current_app)
        register_response = account_service.register(
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.email_addresses.email_address.data.strip(),
            form.passwords.password.data.strip(),
        )

        if register_response.get("status") == 409:
            current_app.logger.info("Email address already in use")
            form.email_addresses.errors = {
                "email_addresses": [_("There is an existing account for %(email)s, try again",
                                      email=form.email_addresses.email_address.data.strip())]}
        elif register_response.get("status") == 400 and register_response.get("message") == "Password is blacklisted":
            form.passwords.errors = {"passwords": [_("This password is not secure enough")]}
            current_app.logger.info("Password is blacklisted")
        else:
            user_id = register_response.get("data").get("id")
            session["registered_email"] = form.email_addresses.email_address.data.strip()
            AuditAPIService.audit_event("User Registration Submitted", origin_id=user_id)

            return redirect(url_for("account_admin.check_your_email"))

    return render_template("register.html", form=form)


@account_admin.route("/register/check-your-email")
def check_your_email():
    current_app.logger.info("Register check your email page")
    if "registered_email" not in session:
        return redirect(url_for("account_admin.register"))

    current_app.logger.info("Rendering registration email sent confirmation page")
    return render_template("check-your-email.html", email=session["registered_email"])


@account_admin.route("/register/resend-activation-email")
def resend_activation_email():
    current_app.logger.info("Resending activation email")
    if "registered_email" not in session:
        return redirect(url_for("sign_in.handle_sign_in"))
    account_service = AccountApiService(current_app)
    result = account_service.resend_email(session["registered_email"])
    if result.status_code not in [200, 404]:
        raise ApplicationError("Failed to resend activation email", "FREACT01", 500)
    return redirect(url_for("account_admin.check_your_email"))


@account_admin.route("/account/activate/<activate_token>")
def activate_account(activate_token):
    current_app.logger.info("Activate account")
    account_service = AccountApiService(current_app)
    token_info = account_service.validate_token(activate_token)
    if token_info and token_info["status"] == "Valid" and token_info["action"] == "activation":
        result = account_service.activate_user(activate_token, token_info["user_id"])
        if result.status_code == 200:
            return render_template("account-activated.html")
        else:
            raise ApplicationError("Account activation failed", "ACAC01", 500)
    elif token_info and token_info["status"] == "Used" and token_info["action"] == "activation" and \
            token_info["user_status"] == "Active":
        return render_template("account-activated.html")
    elif token_info and token_info["status"] == "Expired":
        return redirect(url_for("account_admin.expired_activation", page_type='expired-activation'))
    return redirect(url_for('account_admin.expired_activation', page_type='invalid-activation'))


@account_admin.route("/account/password-check-your-email")
def password_check_your_email():
    current_app.logger.info("Password check your email page")
    if "registered_email" not in session:
        return redirect(url_for("sign_in.handle_sign_in"))

    current_app.logger.info("Rendering registration email sent confirmation page")
    return render_template("password-check-your-email.html", email=session["registered_email"])


@account_admin.route("/account/resend-reset-password")
def resend_reset_password():
    current_app.logger.info("Resending reset password email")
    if "registered_email" not in session:
        return redirect(url_for("sign_in.handle_sign_in"))
    account_service = AccountApiService(current_app)
    account_service.request_reset_password_email(session["registered_email"])
    return redirect(url_for("account_admin.password_check_your_email"))


@account_admin.route("/account/<any('expired-activation', 'invalid-activation'):page_type>", methods=["GET", "POST"])
def expired_activation(page_type):
    current_app.logger.info("Expired or invalid activation")
    form = ExpiredActivationForm()

    if form.validate_on_submit():
        current_app.logger.info("Valid expired activation form")

        account_service = AccountApiService(current_app)
        result = account_service.resend_email(form.email_address.data.strip())

        if result.status_code not in [200, 404]:
            raise ApplicationError("Failed to send email", "EXPACTRE01", 500)
        else:
            session["registered_email"] = form.email_address.data.strip()
            AuditAPIService.audit_event("Account activation submitted", origin_id=form.email_address.data.strip())

            return redirect(url_for("account_admin.check_your_email"))

    if page_type == "expired-activation":
        return render_template("expired-activation.html", form=form)
    return render_template("invalid-activation.html", form=form)


@account_admin.route("/account/change-password/<password_token>", methods=["GET", "POST"])
def change_password_with_token(password_token):
    current_app.logger.info("Change password page")

    form = ChangePasswordWithTokenForm()

    account_service = AccountApiService(current_app)
    token_info = account_service.validate_token(password_token)
    if token_info and token_info["status"] == "Valid" and token_info["action"] == "password":
        if form.validate_on_submit():
            current_app.logger.info("Valid change password with token form")

            password_response = account_service.set_password(
                password_token, token_info["user_id"], form.passwords.password.data.strip()
            )

            if password_response.status_code == 400 and "Password is blacklisted" in password_response.text:
                form.passwords.errors = {"passwords": [_("This password is not secure enough")]}
                current_app.logger.info("Password is blacklisted")
            elif password_response.status_code != 200:
                raise ApplicationError("Failed to change password", "CHPWF01", 500)
            else:
                AuditAPIService.audit_event(
                    "Password changed",
                    supporting_info={"account_affected": token_info["user_id"]},
                    origin_id=token_info["user_id"],
                )
                current_app.logger.info("Password changed")
                flash(_("Your password has been changed"), category="success")
                return redirect(url_for("sign_in.handle_sign_in"))
    elif token_info and token_info["status"] == "Expired":
        return redirect(url_for("account_admin.reset_password", page_type="expired-password-link"))
    else:
        return redirect(url_for("account_admin.reset_password", page_type="invalid-password-link"))

    return render_template("change-password-with-token.html", form=form)


@account_admin.route("/account/<any('expired-password-link', 'reset-password', 'invalid-password-link'):page_type>",
                     methods=["GET", "POST"])
def reset_password(page_type):
    current_app.logger.info("Reset password link expired")
    form = ResetPasswordForm()

    if form.validate_on_submit():
        current_app.logger.info("Valid reset password form")

        account_service = AccountApiService(current_app)
        reset_response = account_service.request_reset_password_email(form.email_address.data.strip())

        if reset_response.status_code not in [201, 404]:
            raise ApplicationError("Failed to send email", "PRF01", 500)
        else:
            session["registered_email"] = form.email_address.data.strip()
            AuditAPIService.audit_event("Password Reset Submitted", origin_id=form.email_address.data.strip())

            return redirect(url_for("account_admin.password_check_your_email"))

    if page_type == "expired-password-link":
        return render_template("expired-password-link.html", form=form)
    elif page_type == "invalid-password-link":
        return render_template("invalid-password-link.html", form=form)
    return render_template("reset-password.html", form=form)
