import re
from datetime import datetime

from cryptography.fernet import Fernet
from dateutil.relativedelta import relativedelta
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_babel import lazy_gettext as _
from landregistry.exceptions import ApplicationError

from server.dependencies.account_api.account_api_service import AccountApiService
from server.dependencies.audit_api.audit_api_service import AuditAPIService
from server.dependencies.authentication_api import AuthenticationApi
from server.dependencies.gov_pay.gov_pay_service import GovPayService
from server.dependencies.search_local_land_charge_api.search_local_land_charge_service import (
    SearchLocalLandChargeService,
)
from server.models.searches import PaymentState, SearchState
from server.services.check_migration_status import CheckMigrationStatus
from server.services.datetime_formatter import format_date
from server.services.paid_search_utils import PaidSearchUtils
from server.services.search_utilities import calculate_pagination_info
from server.views.auth import authenticated
from server.views.forms.change_details_form import ChangeDetailsForm
from server.views.forms.change_password_form import ChangePasswordForm
from server.views.forms.search_free_searches_form import SearchFreeSearchesForm
from server.views.forms.search_searches_form import SearchSearchesForm
from server.views.search import search_by_area

my_account = Blueprint("my_account", __name__, template_folder="../templates/my-account")
my_account.add_app_template_filter(PaidSearchUtils.format_search_id, "format_search_id")


SEARCHES_PER_PAGE = 15


@my_account.route("/account/my-account")
@authenticated
def my_account_page():
    current_app.logger.info("My account page")

    service_messages = SearchLocalLandChargeService(current_app.config).get_service_messages()
    if service_messages:
        flash(service_messages, "service_message")

    return render_template(
        "my-account.html",
        first_name=session["jwt_payload"].principle.first_name,
        surname=session["jwt_payload"].principle.surname,
    )


@my_account.route("/account/change-details", methods=["GET", "POST"])
@authenticated
def change_details():
    current_app.logger.info("Change details page")

    form = ChangeDetailsForm(
        first_name=session["jwt_payload"].principle.first_name,
        last_name=session["jwt_payload"].principle.surname,
    )

    if form.validate_on_submit():
        current_app.logger.info("Valid change details form")

        account_service = AccountApiService(current_app)
        reset_response = account_service.change_name(form.first_name.data.strip(), form.last_name.data.strip())

        if reset_response.status_code != 200:
            raise ApplicationError("Failed to change details", "ACCHNG01", 500)
        else:
            AuditAPIService.audit_event(
                "Account details changed",
                origin_id=session["jwt_payload"].principle.principle_id,
            )
            # Change name in session so seen immediately
            session["jwt_payload"].principle.first_name = form.first_name.data.strip()
            session["jwt_payload"].principle.surname = form.last_name.data.strip()
            flash(
                _("Your account details have been successfully changed"),
                category="success",
            )

            return redirect(url_for("my_account.my_account_page"))

    return render_template(
        "change-details.html",
        form=form,
    )


@my_account.route("/account/change-password", methods=["GET", "POST"])
@authenticated
def change_password():
    current_app.logger.info("Change password page")

    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_app.logger.info("Valid change password form")

        authentication_api = AuthenticationApi()
        authenticated, result = authentication_api.authenticate(form.current_password.data.strip())
        if not authenticated:
            form.current_password.errors.append(_("Current password is not correct"))
        else:
            account_service = AccountApiService(current_app)
            password_response = account_service.change_password(form.new_passwords.new_password.data.strip())

            if password_response.status_code == 400 and "Password is blacklisted" in password_response.text:
                form.new_passwords.errors = {"new_passwords": _("This password is not secure enough")}
                current_app.logger.info("Password is blacklisted")
            elif password_response.status_code != 200:
                raise ApplicationError("Failed to change password", "CHPWF01", 500)
            else:
                AuditAPIService.audit_event(
                    "Password changed",
                    supporting_info={"account_affected": session["profile"]["user_id"]},
                    origin_id=session["profile"]["user_id"],
                )
                current_app.logger.info("Password changed")
                flash(_("Your password has been changed"), category="success")
                return redirect(url_for("my_account.my_account_page"))

    return render_template("change-password.html", form=form)


@my_account.route("/account/active-searches")
@authenticated
def active_searches():
    current_app.logger.info("Active searches page")
    form = SearchSearchesForm(search_term=request.args.get("search_term"))

    display_page = request.args.get("page", 1, type=int)

    search_llc_service = SearchLocalLandChargeService(current_app.config)
    all_searches = search_llc_service.get_paid_search_items(session["profile"]["user_id"])

    searches = []

    # Loop through each of the user's searches and get the expired ones
    for search in all_searches:
        search_llc_service.check_for_completed_doc_url(search)
        # Ignore searches that still have no document_urls because in progress or weird
        if not search.document_url:
            continue
        if search.lapsed_date is None:
            if search.repeat_searches:
                for repeated_search in search.repeat_searches:
                    search_llc_service.check_for_completed_doc_url(repeated_search)
            # searches will have no lapsed date so add one in now to display the date on which it will lapse
            search.lapsed_date = search.search_date.replace(tzinfo=None) + relativedelta(months=+6)

            searches.append(search)

    if (request.args.get("submit") == "y" and form.validate()) or (form.search_term.data and form.validate()):
        matching_searches, expand = search_in_searches(form.search_term.data.strip(), searches)

        display_searches, pagination_info, start_index = calculate_pagination_info(
            matching_searches,
            "my_account.active_searches",
            SEARCHES_PER_PAGE,
            display_page,
            {"search_term": request.args.get("search_term")},
        )

        return render_template(
            "active-searches.html",
            display_searches=display_searches,
            show_pagination=len(matching_searches) > SEARCHES_PER_PAGE,
            start_index=start_index,
            pagination_info=pagination_info,
            result_count=len(matching_searches),
            form=form,
            expand=expand,
        )

    display_searches, pagination_info, start_index = calculate_pagination_info(
        searches,
        "my_account.active_searches",
        SEARCHES_PER_PAGE,
        display_page,
        {"search_term": request.args.get("search_term")},
    )

    return render_template(
        "active-searches.html",
        display_searches=display_searches,
        show_pagination=len(searches) > SEARCHES_PER_PAGE,
        start_index=start_index,
        pagination_info=pagination_info,
        result_count=len(searches),
        form=form,
    )


@my_account.route("/account/view-search/<search_id>")
@authenticated
def view_search(search_id):
    search_llc_service = SearchLocalLandChargeService(current_app.config)
    paid_search = search_llc_service.get_paid_search_item(session["profile"]["user_id"], search_id)

    f = Fernet(current_app.config["GEOSERVER_SECRET_KEY"])
    enc_search_id = f.encrypt(f"view_{paid_search.search_id}".encode()).decode()

    search_state = SearchState(search_reference=paid_search.search_id)
    search_state.previously_completed = True
    search_state.charges = []

    if session.get("paid_searches", None) is None:
        session["paid_searches"] = {}
    session["paid_searches"][enc_search_id] = {
        "paid_search_item": paid_search,
        "search_state": search_state,
    }
    session.modified = True

    return redirect(url_for("paid_search.get_paid_search", enc_search_id=enc_search_id))


@my_account.route("/account/expired-searches")
@authenticated
def expired_searches():
    current_app.logger.info("Expired searches page")
    form = SearchSearchesForm(search_term=request.args.get("search_term"))

    display_page = request.args.get("page", 1, type=int)

    search_llc_service = SearchLocalLandChargeService(current_app.config)
    all_searches = search_llc_service.get_paid_search_items(session["profile"]["user_id"])

    searches = []

    # Loop through each of the user's searches and get the expired ones
    for search in all_searches:
        if search.lapsed_date is not None:
            searches.append(search)

    # If we're searching then find things that match
    if (request.args.get("submit") == "y" and form.validate()) or (form.search_term.data and form.validate()):
        matching_searches, expand = search_in_searches(form.search_term.data.strip(), searches)

        display_searches, pagination_info, start_index = calculate_pagination_info(
            matching_searches,
            "my_account.expired_searches",
            SEARCHES_PER_PAGE,
            display_page,
            {"search_term": request.args.get("search_term")},
        )

        return render_template(
            "expired-searches.html",
            display_searches=display_searches,
            show_pagination=len(matching_searches) > SEARCHES_PER_PAGE,
            start_index=start_index,
            pagination_info=pagination_info,
            result_count=len(matching_searches),
            form=form,
            expand=expand,
        )

    display_searches, pagination_info, start_index = calculate_pagination_info(
        searches,
        "my_account.expired_searches",
        SEARCHES_PER_PAGE,
        display_page,
        {"search_term": request.args.get("search_term")},
    )

    return render_template(
        "expired-searches.html",
        display_searches=display_searches,
        show_pagination=len(searches) > SEARCHES_PER_PAGE,
        start_index=start_index,
        pagination_info=pagination_info,
        result_count=len(searches),
        form=form,
    )


@my_account.route("/account/repeat-search/<search_id>")
@authenticated
def repeat_search(search_id):
    search_llc_service = SearchLocalLandChargeService(current_app.config)
    parent_search = search_llc_service.get_paid_search_item(session["profile"]["user_id"], search_id)

    if parent_search.lapsed_date and not parent_search.request_repeat:
        raise ApplicationError(
            f"Cannot repeat search with id: {search_id} because it has lapsed.",
            "SRHLPD01",
            500,
        )

    current_app.logger.info("Checking refund status of search id {} for repeat".format(search_id))

    # call gov pay api to check if the search they requested to repeat has been refunded
    gov_pay_service = GovPayService(current_app.config)
    payment_status = gov_pay_service.get_payment(parent_search.payment_id)

    if payment_status["refund_summary"]["status"].upper() == "FULL":
        # is refunded so show results page
        current_app.logger.warning(f"Cannot repeat search with id: {search_id} because it has been refunded")
        messages = [
            _("You cannot request a repeat on this search as it has been refunded to you."),
            _("You can request and download another official search result."),
            _(
                "Official search results are &pound;%(search_fee)s.",
                search_fee="{:.2f}".format(int(current_app.config["SEARCH_FEE_IN_PENCE"]) / 100),
            ),
        ]
        flash("<br>".join([str(message) for message in messages]))

        return redirect(url_for("my_account.paid_search_review", search_id=search_id))
    else:
        session.pop("repeated_search", None)

    current_app.logger.info("repeating search with id {}".format(search_id))

    migration_status = CheckMigrationStatus.process(parent_search.search_extent)

    if migration_status["flag"] == "fail_maintenance" or migration_status["flag"] == "fail_maintenance_contact":
        session["authority_data"] = migration_status
        return redirect(url_for("search.no_information_available"))
    elif migration_status["flag"] != "pass" and migration_status["flag"] != "warning":
        # This should never happen so just throw error
        raise ApplicationError(
            f"Cannot repeat search with id: {search_id} migration check flag {migration_status['flag']} is invalid",
            "MIGINV01",
            500,
        )

    charges = PaidSearchUtils.search_by_area(parent_search.search_extent)

    f = Fernet(current_app.config["GEOSERVER_SECRET_KEY"])
    enc_search_id = f.encrypt(f"repeat_{search_id}".encode()).decode()

    if session.get("paid_searches", None) is None:
        session["paid_searches"] = {}

    session["paid_searches"][enc_search_id] = {
        "payment_state": PaymentState(
            parent_search.payment_id,
            parent_search.search_area_description,
            {},
            "N/A",
            0,
            None,
            None,
        ),
        "search_state": SearchState(
            parent_search.search_extent,
            charges,
            parent_search.search_area_description,
            parent_search.search_id,
            None,
        ),
    }

    AuditAPIService.audit_event("Repeated search", supporting_info={"search_id": parent_search.search_id})

    # remove the flag for repeating the search, in case it exists. If not, will not cause issues
    search_llc_service.remove_paid_search_repeat_request(search_id)

    current_app.logger.info("redirecting to paid search summary page")

    return redirect(url_for("paid_search.get_paid_search", enc_search_id=enc_search_id))


@my_account.route("/account/repeat-expired-search/<search_id>")
@authenticated
def paid_search_review(search_id):
    search_llc_service = SearchLocalLandChargeService(current_app.config)
    paid_search = search_llc_service.get_paid_search_item(session["profile"]["user_id"], search_id)

    AuditAPIService.audit_event(
        "Free search Performed via Review and Pay lapsed search",
        supporting_info={"search_id": paid_search.search_id},
    )

    return search_by_area(paid_search.search_extent, paid_search.search_area_description)


def search_in_searches(search_term, searches):
    matching_searches = []
    search_term_no_whitespace = re.sub(r"\s+", "", search_term)
    if search_term_no_whitespace.isdecimal():
        search_term_id = search_term_no_whitespace
    else:
        search_term_id = None

    expand = []
    for search in searches:
        repeat_ids = ["{:0>9}".format(repeat.search_id) for repeat in search.repeat_searches]
        if search_term_id is not None:
            if str(search_term_id) in " ".join(repeat_ids):
                search.repeat_found = True
                expand.append(search.search_id)
                matching_searches.append(search)
                continue
            if str(search_term_id) in "{:0>9}".format(search.search_id):
                matching_searches.append(search)
                continue
        if search_term.lower() in search.search_area_description.lower():
            matching_searches.append(search)

    return matching_searches, expand


@my_account.route("/account/free-searches", methods=["GET", "POST"])
@authenticated
def free_searches():
    current_app.logger.info("Free searches page")
    form = SearchFreeSearchesForm(search_term=request.args.get("search_term"))

    display_page = request.args.get("page", 1, type=int)

    search_llc_service = SearchLocalLandChargeService(current_app.config)

    if form.validate_on_submit():
        search = search_llc_service.get_free_search_for_user_by_search_id(
            session["profile"]["user_id"], form.search_term.data.strip()
        )
        if not search:
            form.search_term.errors.append(_("You have entered an invalid Search ID. Check it and try again"))
        else:
            search[0]["formatted_date"] = format_date(datetime.fromisoformat(search[0]["search-date"]))
            return render_template(
                "free-searches.html",
                searches=search,
                show_pagination=False,
                start_index=0,
                pagination_info=None,
                result_count=1,
                form=form,
            )

    free_search_results = search_llc_service.get_free_search_items(
        session["profile"]["user_id"], SEARCHES_PER_PAGE, display_page
    )

    display_searches, pagination_info, start_index = calculate_pagination_info(
        None,
        "my_account.free_searches",
        SEARCHES_PER_PAGE,
        display_page,
        no_of_pages=free_search_results["pages"],
        no_of_items=free_search_results["total"],
    )

    for search in free_search_results["items"]:
        search["formatted_date"] = format_date(datetime.fromisoformat(search["search-date"]))

    return render_template(
        "free-searches.html",
        searches=free_search_results["items"],
        show_pagination=free_search_results["total"] > SEARCHES_PER_PAGE,
        start_index=start_index,
        pagination_info=pagination_info,
        result_count=free_search_results["total"],
        form=form,
    )


@my_account.route("/account/searches-to-repeat", methods=["GET"])
@authenticated
def searches_to_repeat_top():
    current_app.logger.info("Searches to repeat top page")

    search_llc_service = SearchLocalLandChargeService(current_app.config)

    free_search_results = search_llc_service.get_free_search_items_to_repeat(
        session["profile"]["user_id"], SEARCHES_PER_PAGE, 1
    )
    paid_search_results = search_llc_service.get_paid_search_items_to_repeat(
        session["profile"]["user_id"], SEARCHES_PER_PAGE, 1
    )

    return render_template(
        "searches-to-repeat.html",
        free_searches_count=free_search_results["total"],
        paid_searches_count=paid_search_results["total"],
    )


@my_account.route("/account/paid-searches-to-repeat", methods=["GET"])
@authenticated
def paid_searches_to_repeat():
    current_app.logger.info("Paid searches to repeat page")

    display_page = request.args.get("page", 1, type=int)

    search_llc_service = SearchLocalLandChargeService(current_app.config)

    paid_search_results = search_llc_service.get_paid_search_items_to_repeat(
        session["profile"]["user_id"], SEARCHES_PER_PAGE, display_page
    )

    display_searches, pagination_info, start_index = calculate_pagination_info(
        None,
        "my_account.paid_searches_to_repeat",
        SEARCHES_PER_PAGE,
        display_page,
        no_of_pages=paid_search_results["pages"],
        no_of_items=paid_search_results["total"],
    )

    for search in paid_search_results["items"]:
        search["formatted_date"] = format_date(datetime.fromisoformat(search["search-date"]))

    return render_template(
        "paid-searches-to-repeat.html",
        searches=paid_search_results["items"],
        show_pagination=paid_search_results["total"] > SEARCHES_PER_PAGE,
        start_index=start_index,
        pagination_info=pagination_info,
        result_count=paid_search_results["total"],
    )


@my_account.route("/account/free-searches-to-repeat", methods=["GET"])
@authenticated
def free_searches_to_repeat():
    current_app.logger.info("Free searches to repeat page")

    display_page = request.args.get("page", 1, type=int)

    search_llc_service = SearchLocalLandChargeService(current_app.config)

    free_search_results = search_llc_service.get_free_search_items_to_repeat(
        session["profile"]["user_id"], SEARCHES_PER_PAGE, display_page
    )

    display_searches, pagination_info, start_index = calculate_pagination_info(
        None,
        "my_account.free_searches_to_repeat",
        SEARCHES_PER_PAGE,
        display_page,
        no_of_pages=free_search_results["pages"],
        no_of_items=free_search_results["total"],
    )

    for search in free_search_results["items"]:
        search["formatted_date"] = format_date(datetime.fromisoformat(search["search-date"]))

    return render_template(
        "free-searches-to-repeat.html",
        searches=free_search_results["items"],
        show_pagination=free_search_results["total"] > SEARCHES_PER_PAGE,
        start_index=start_index,
        pagination_info=pagination_info,
        result_count=free_search_results["total"],
    )


@my_account.route("/account/repeat-free-search/<search_id>")
@authenticated
def free_search_review(search_id):
    search_llc_service = SearchLocalLandChargeService(current_app.config)
    search = search_llc_service.get_free_search_for_user_by_search_id(session["profile"]["user_id"], search_id)

    if not search:
        raise ApplicationError("Free search not found", "FSNF01", 404)

    AuditAPIService.audit_event(
        "Free Search Performed via free searches page",
        supporting_info={"search_id": search_id},
    )

    # remove the flag for repeating the search, in case it exists. If not, will not cause issues
    search_llc_service.remove_free_search_repeat_request(search_id)

    return search_by_area(search[0]["search-extent"], search[0]["address"])
