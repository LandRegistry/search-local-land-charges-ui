from datetime import datetime
import json
from urllib.parse import unquote_plus
import uuid
from flask import Blueprint, render_template, current_app, send_file, url_for, redirect, request, session
from server import config
from server.dependencies.audit_api.audit_api_service import AuditAPIService
from server.dependencies.storage_api.storage_api_service import StorageAPIService
from server.models.searches import PaymentState
from server.services.back_link_history import clear_history
from server.services.charge_id_utils import calc_display_id
from server.services.paid_results.paid_results_converter import PaidResultsConverter
from server.services.paid_search_utils import PaidSearchUtils
from server.services.search_by_area import SearchByArea
from server.views.auth import authenticated
from server.services.fee_functions import format_fee_for_gov_pay
from landregistry.exceptions import ApplicationError
from server.services.search_utilities import calculate_pagination_info, decode_validate_search_id, get_charge_items
from server.services.search_by_postcode import SearchByPostcode
from server.dependencies.gov_pay.gov_pay_service import GovPayService
from flask_babel import gettext as _
from server.views.forms.confirm_address_form import ConfirmAddressForm

from server.views.forms.search_area_description_form import SearchAreaDescriptionForm

paid_search = Blueprint("paid_search", __name__, url_prefix="/paid-search", template_folder="../templates/paid-search")


@paid_search.route("/<enc_search_id>/search-area-description", methods=["GET", "POST"])
@authenticated
def search_area_description(enc_search_id):
    current_app.logger.info("Loading search area description")

    search_state = decode_validate_search_id(enc_search_id)

    if not search_state:
        return redirect(url_for("search.search_by_post_code_address"))

    if search_state.address:
        return redirect(url_for('paid_search.confirm_address', enc_search_id=enc_search_id))

    form = SearchAreaDescriptionForm()

    if request.args.get("address"):
        form.has_address.data = 'find_address'
        address_string = unquote_plus(request.args.get("address"))
        # Should never happen without hacking
        if len(address_string) > 1000:
            raise ApplicationError("Address has  over 1000 characters", "ADDR01", 500)
        form.selected_address.data = address_string

    address_list = []

    if form.validate_on_submit():
        if form.find.data:
            address_list = search_description_find(form)
        else:
            continue_result = search_description_continue(form, search_state, enc_search_id)
            if continue_result:
                return continue_result

    return render_template(
        "search-area-description.html",
        geometry=json.dumps(search_state.search_extent),
        enc_search_id=enc_search_id,
        form=form,
        address_list=address_list
    )


@paid_search.route("/<enc_search_id>/confirm-address", methods=["GET", "POST"])
@authenticated
def confirm_address(enc_search_id):
    current_app.logger.info("Loading address confirm")

    search_state = decode_validate_search_id(enc_search_id)

    if not search_state:
        return redirect(url_for("search.search_by_post_code_address"))

    form = ConfirmAddressForm()

    if form.validate_on_submit():
        if form.address_matches.data == 'yes':
            return continue_to_payment(search_state.address, search_state, enc_search_id)
        elif form.address_matches.data == 'no':
            if form.search_area_description.data is None or form.search_area_description.data.strip() == "":
                form.search_area_description.errors.append(_("Describe the search location"))
            else:
                return continue_to_payment(form.search_area_description.data.strip(), search_state, enc_search_id)

    return render_template(
        "confirm-address.html",
        geometry=json.dumps(search_state.search_extent),
        enc_search_id=enc_search_id,
        form=form,
        address=search_state.address
    )


def search_description_find(form):
    address_list = []
    form.selected_address.data = None
    if form.search_postcode.data is None or form.search_postcode.data.strip() == "":
        form.search_postcode.errors.append(_("Enter a postcode"))
    else:
        results = SearchByPostcode(current_app.logger).process(form.search_postcode.data.strip(),
                                                               current_app.config)
        if results['status'] == 'error':
            form.search_postcode.errors.append(results['search_message'])
        else:
            address_list = [result['address'] for result in results['data']]
    return address_list


def search_description_continue(form, search_state, enc_search_id):
    if form.has_address.data == "find_address":
        if form.selected_address.data is None or form.selected_address.data.strip() == "":
            form.search_postcode.errors.append(
                _("Enter a postcode, select ‘Find address’ and choose an address from the list"))
        else:
            return continue_to_payment(form.selected_address.data, search_state, enc_search_id)
    else:
        if form.search_area_description.data is None or form.search_area_description.data.strip() == "":
            form.search_area_description.errors.append(_("Describe the search location"))
        else:
            return continue_to_payment(form.search_area_description.data, search_state, enc_search_id)
    return None


def continue_to_payment(search_area_description, search_state, enc_search_id):
    gov_pay_service = GovPayService(current_app.config)
    reference_num = str(uuid.uuid4()).upper()[:6]

    payment_request = gov_pay_service.request_payment(format_fee_for_gov_pay(config.SEARCH_FEE_IN_PENCE),
                                                      reference_num,
                                                      _("Official search result of local land charges"),
                                                      enc_search_id)
    payment_state = PaymentState.from_json(payment_request)

    search_state.address = search_area_description

    if session.get('paid_searches', None) is None:
        session['paid_searches'] = {}
    # Trying to minimise the amount of info in the session here until payment taken
    session['paid_searches'][enc_search_id] = {'payment_state': payment_state,
                                               'address': search_state.address}
    session.modified = True

    return redirect(payment_request['_links']['next_url']['href'])


@paid_search.route("/<enc_search_id>/process-pay")
@authenticated
def process_pay(enc_search_id):
    current_app.logger.info("Processing payment")

    # Reset history since we can't go back from here really
    clear_history()

    search_session = session['paid_searches'][enc_search_id]

    if search_session['payment_state'].payment_id is None:
        raise ApplicationError("Unable to find associated payment id", "PAY01", 500)

    gov_pay_service = GovPayService(current_app.config)
    payment_status = gov_pay_service.get_payment(search_session['payment_state'].payment_id)

    payment_state = PaymentState.from_json(payment_status)
    search_session['payment_state'] = payment_state
    # Reset search reference to make sure since processing a new payment
    if 'search_state' in search_session:
        search_session['search_state'].search_reference = None
    search_session.pop('paid_search_item', None)

    session.modified = True

    if payment_state.state['status'] == 'success':
        # Payment is successful so recreate all the session stuff
        search_session['search_state'] = decode_validate_search_id(enc_search_id)
        search_session['search_state'].address = search_session['address']
        search_by_area_processor = SearchByArea(current_app.logger, current_app.config)
        response = search_by_area_processor.process(search_session['search_state'].search_extent,
                                                    results_filter='cancelled')
        if response['status'] not in [200, 404]:
            raise ApplicationError("Failed to retrieve charges", "PAYC01", 500)

        current_app.logger.info("Charges found")
        search_session['search_state'].charges = get_charge_items(response.get('data', []))

        return redirect(url_for('paid_search.get_paid_search', enc_search_id=enc_search_id))
    elif payment_state.state['status'] in ('cancelled', 'error'):
        return redirect(url_for('index.index_page'))
    else:
        # catch both 'failed' status and any other unexpected result
        return redirect(url_for('search_results.results'))


@paid_search.route("/<enc_search_id>/paid-search")
@authenticated
def get_paid_search(enc_search_id):
    current_app.logger.info("Paid search page requested")

    search_session = session['paid_searches'][enc_search_id]

    refresh = search_session['search_state'].parent_search is not None
    prev_completed = search_session['search_state'].previously_completed is True

    if not prev_completed and not refresh and (search_session['payment_state'].payment_id is None
                                               or search_session['payment_state'].state['status'] != "success"
                                               or session['profile']['user_id'] is None):
        raise ApplicationError(
            f"Unable to find successful payment with id {search_session['payment_state'].payment_id}",
            "PAY02", 500)

    if search_session['search_state'].search_reference is None:

        contact_id = session['profile']['user_id']

        search_ref = PaidSearchUtils.request_search_generation(search_session['search_state'].search_extent,
                                                               search_session['search_state'].address,
                                                               search_session['search_state'].parent_search,
                                                               contact_id=contact_id)
        PaidSearchUtils.pre_associate_search(search_ref,
                                             search_session['payment_state'].payment_id,
                                             search_session['search_state'].search_extent,
                                             search_session['search_state'].address,
                                             search_session['search_state'].charges,
                                             search_session['payment_state'].payment_provider,
                                             search_session['payment_state'].card_brand,
                                             search_session['payment_state'].amount,
                                             search_session['payment_state'].reference,
                                             search_session['search_state'].parent_search)
        search_session['search_state'].search_reference = search_ref
        session.modified = True

        return render_template('payment-success.html', payment_state=search_session['payment_state'], refresh=refresh,
                               enc_search_id=enc_search_id)

    paid_search = search_session.get('paid_search_item', None)
    if not paid_search:
        try:
            paid_search = PaidSearchUtils.get_search_result(search_session['search_state'].search_reference,
                                                            search_session['payment_state'].payment_id,
                                                            search_session['search_state'].search_extent,
                                                            search_session['search_state'].address,
                                                            search_session['search_state'].charges,
                                                            search_session['payment_state'].payment_provider,
                                                            search_session['payment_state'].card_brand,
                                                            search_session['payment_state'].amount,
                                                            search_session['payment_state'].reference,
                                                            search_session['search_state'].parent_search)
        except Exception:
            raise ApplicationError("Failed to get paid search results", "PAYPDF01", 500)
    if not paid_search:
        return render_template('paid-search-query.html', payment_state=search_session['payment_state'],
                               refresh=refresh, reload_time=config.PDF_GENERATION_POLL, enc_search_id=enc_search_id)

    search_session['paid_search_item'] = paid_search
    session.modified = True

    AuditAPIService.audit_event("Paid Search Performed", supporting_info={
        'gov-pay-id': paid_search.payment_id,
        'reference': paid_search.reference
    })

    storage_api_service = StorageAPIService(current_app.config)

    total_charges = 0
    if paid_search.charges is not None:
        total_charges = len(paid_search.charges)

    has_supporting_documents = False
    if paid_search.charges:
        for charge in paid_search.charges:
            if "documents-filed" in charge:
                has_supporting_documents = True
                break

    external_document_url = storage_api_service.get_external_url_for_document_url(paid_search.document_url)

    return render_template('paid-search-summary.html',
                           total_charges=total_charges,
                           geometry=json.dumps(paid_search.search_extent),
                           document_url=external_document_url,
                           search_area=paid_search.search_area_description,
                           payment_reference=paid_search.reference,
                           search_reference=PaidSearchUtils.format_search_id(paid_search.search_id),
                           maintenance=False,
                           has_supporting_documents=has_supporting_documents, enc_search_id=enc_search_id)


@paid_search.route("/pdf-poll-failure")
@authenticated
def pdf_poll_failure():
    raise ApplicationError('PDF polling failure', "PAYPDF01", 500)


@paid_search.route('/<enc_search_id>/download')
@authenticated
def download_charges(enc_search_id):
    search_session = session['paid_searches'][enc_search_id]
    download_format = request.args.get('download_format')
    charges = search_session['paid_search_item'].charges
    date = datetime.now().strftime('%d%b%y:%H:%M')

    if "json" == download_format:
        json_file = PaidResultsConverter.to_json(charges)
        return send_file(json_file, mimetype="application/json",
                         download_name="LocalLandCharges_{}.json".format(date), as_attachment=True)
    elif 'csv' == download_format:
        csvfile = PaidResultsConverter.to_csv(charges)
        return send_file(csvfile, mimetype="text/csv",
                         download_name="LocalLandCharges_{}.csv".format(date), as_attachment=True)
    elif "xml" == download_format:
        xml_file = PaidResultsConverter.to_xml(charges)
        return send_file(xml_file, mimetype="application/xml",
                         download_name="LocalLandCharges_{}.xml".format(date), as_attachment=True)
    else:
        current_app.logger.error("Requested format not supported.")
        raise ApplicationError("Requested format not supported.", "DWNFMT01", 500)


@paid_search.route('/<enc_search_id>/supporting_documents')
@authenticated
def supporting_document_list(enc_search_id):
    current_app.logger.info("Listing supporting documents")

    search_session = session['paid_searches'][enc_search_id]

    current_page = int(request.args.get("page", 1))

    if 'paid_search_item' not in search_session:
        current_app.logger.error("No paid search found in session, redirecting back to beginning of search")
        return redirect(url_for('search.search_by_post_code_address'))

    charges = [calc_display_id(charge['local-land-charge'])
               for charge in search_session['paid_search_item'].charges
               if "documents-filed" in charge and len(charge['documents-filed'].keys()) > 0]
    charges.sort()

    display_charges, pagination_info, start_index = \
        calculate_pagination_info(charges, 'paid_search.supporting_document_list', config.DEFAULT_PAGE_SIZE,
                                  current_page, {"enc_search_id": enc_search_id})

    return render_template('supporting-document-list.html',
                           charges=display_charges,
                           total_charges=len(charges),
                           show_pagination=len(charges) > config.DEFAULT_PAGE_SIZE,
                           pagination_info=pagination_info,
                           start_index=start_index,
                           enc_search_id=enc_search_id)


@paid_search.route('/<enc_search_id>/supporting_documents/<charge_id>')
@authenticated
def charge_supporting_documents(enc_search_id, charge_id):
    current_app.logger.info("Retrieving supporting documents for charge {}".format(charge_id))

    search_session = session['paid_searches'][enc_search_id]

    if 'paid_search_item' not in search_session:
        current_app.logger.error("No paid search found in session, redirecting back to beginning of search")
        return redirect(url_for('search.search_by_post_code_address'))

    charges_with_docs = {}

    for charge in search_session['paid_search_item'].charges:
        if "documents-filed" in charge and len(charge['documents-filed'].keys()) > 0:
            charges_with_docs[calc_display_id(charge['local-land-charge'])] = charge['documents-filed']

    if charge_id not in charges_with_docs:
        raise ApplicationError("Charge does not have documents", "CHDOC01", 404)

    storage_api_service = StorageAPIService(current_app.config)

    # Assume that all the documents have the same subdirectory (they should have)
    one_document = list(charges_with_docs[charge_id].values())[0][0]

    documents_url = storage_api_service.get_external_url(
        one_document['subdirectory'], one_document['bucket'])

    return redirect(documents_url)
