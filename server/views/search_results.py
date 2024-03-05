import json
from flask import Blueprint, render_template, current_app, url_for, redirect, request, session
from server import config
from server.views.auth import authenticated
from server.models.charges import LocalLandChargeItem, LandCompensationItem, \
    LightObstructionNoticeItem, FinancialItem
from server.models.common import default_text
from server.services.fee_functions import format_fee_for_display
from server.dependencies.search_api.category_service import CategoryService
from datetime import datetime
from cryptography.fernet import Fernet
from landregistry.exceptions import ApplicationError
from server.services.search_utilities import calculate_pagination_info, decode_validate_search_id
from collections import OrderedDict
from flask_babel import gettext as _

from server.views.forms.search_results_form import SearchResultsForm

try:
    CHARGES_PER_PAGE = int(config.CHARGES_PER_PAGE)
except ValueError:
    CHARGES_PER_PAGE = 25

search_results = Blueprint("search_results", __name__, url_prefix="/search-results",
                           template_folder="../templates/search-results")


@search_results.route('', methods=["GET", "POST"])
@authenticated
def results():
    current_app.logger.info('Loading results page')

    form = SearchResultsForm()

    if form.validate_on_submit():
        search_state = decode_validate_search_id(form.enc_search_id.data)
        if not search_state:
            raise ApplicationError("Invalid encoded search ID", "INENC01", 500)

        return redirect(url_for('paid_search.search_area_description', enc_search_id=form.enc_search_id.data))

    if "search_state" not in session:
        return redirect(url_for('index.index_page'))

    search_extent = session['search_state'].search_extent
    unsorted_charges = []

    if session['search_state'].charges:
        for charge in session['search_state'].charges:
            if "Land compensation" in charge['charge-type']:
                unsorted_charges.append(LandCompensationItem.from_json(charge))
            elif "Light obstruction notice" in charge['charge-type']:
                unsorted_charges.append(LightObstructionNoticeItem.from_json(charge))
            elif "Financial" in charge['charge-type']:
                unsorted_charges.append(FinancialItem.from_json(charge))
            else:
                unsorted_charges.append(LocalLandChargeItem.from_json(charge))
    current_app.logger.info('Sorting Charges')
    charges = sort_charges(unsorted_charges)

    # Encrypt the search ID to prevent tampering
    f = Fernet(current_app.config['GEOSERVER_SECRET_KEY'])
    enc_search_id = f.encrypt(str(session['search_state'].free_search_id).encode()).decode()
    form.enc_search_id.data = enc_search_id

    current_page = request.args.get("page", 1, type=int)

    repeat_search = False
    if 'repeated_search' in session and session['repeated_search']:
        repeat_search = True

    display_charges, pagination_info, start_index = \
        calculate_pagination_info(charges, 'search_results.results', CHARGES_PER_PAGE, current_page)

    return render_template('search-results.html',
                           charges=group_charges_format_for_display(display_charges),
                           geometry=json.dumps(search_extent),
                           total_charges=len(charges),
                           show_pagination=len(pagination_info['items']) > 1,
                           start_index=start_index,
                           pagination_info=pagination_info,
                           enc_search_id=enc_search_id,
                           year=datetime.today().year,
                           search_fee=format_fee_for_display(config.SEARCH_FEE_IN_PENCE),
                           repeat_search=repeat_search,
                           maintenance=False,
                           form=form
                           )


def sort_charges(charges):

    categories = CategoryService(current_app.config).get()
    order = [category['display-name'] for category in categories]

    def category_sort(charge):
        try:
            return order.index(charge.charge_type)
        except ValueError:
            return len(order)

    charges.sort(key=category_sort)

    sorted_charges = [{'group-type': charge.charge_type if charge.charge_type in order else 'Other',
                       'charge': charge}
                      for charge in charges]

    return sorted_charges


def group_charges_format_for_display(charges):
    grouped = OrderedDict()
    for charge in charges:
        grouped.setdefault(charge['group-type'], []).append(format_for_display(charge['charge']))
    return grouped


def format_for_display(charge):
    heading = {}
    content = {}
    if charge.charge_sub_category:
        heading["header"] = charge.format_field_for_display("charge_sub_category")
    else:
        heading["header"] = charge.format_field_for_display("charge_type")
    if charge.supplementary_information:
        heading["sub_header"] = charge.format_field_for_display("supplementary_information")
    else:
        heading["sub_header"] = ""
    if isinstance(charge, LightObstructionNoticeItem):
        format_lon(charge, heading, content)
    else:
        heading["creation_date"] = charge.format_date_for_display("charge_creation_date")
        if charge.charge_geographic_description:
            content[_('Location')] = charge.charge_geographic_description.splitlines()
        else:
            content[_('Location')] = charge.format_charge_address_for_display()
        content[_('Originating authority')] = charge.format_field_for_display('originating_authority')
        content[_('Authority reference')] = charge.format_field_for_display('further_information_reference')
        content[_('Registration date')] = charge.format_date_for_display('registration_date')
        content[_('Law')] = charge.format_field_for_display('statutory_provision')
        content[_('Legal document')] = charge.format_field_for_display('instrument')
        if isinstance(charge, FinancialItem):
            format_financial(charge, content)
        elif isinstance(charge, LandCompensationItem):
            format_land_comp(charge, content)
        content[_('HM Land Registry reference')] = charge.format_llc_ref_for_display('local_land_charge')

    return {"heading": heading, "content": content}


def format_land_comp(charge, content):
    if charge.land_compensation_paid or charge.land_compensation_amount_type or \
            charge.land_capacity_description or charge.amount_of_compensation:
        content[_('Advance payment')] = f"£{charge.format_money_field_for_display('land_compensation_paid')}"
        amount_of_comp = charge.format_money_field_for_display('amount_of_compensation')
        if amount_of_comp != default_text:
            amount_of_comp = f"£{amount_of_comp}"
        content[_('Total compensation')] = amount_of_comp
        content[_('Agreed or estimated')] = charge.format_field_for_display('land_compensation_amount_type')
        content[_('Interest in land')] = charge.format_field_for_display('land_capacity_description')
    if charge.land_sold_description or charge.land_works_particulars:
        content[_('Land sold')] = charge.format_field_for_display('land_sold_description')
        content[_('Work done')] = charge.format_field_for_display('land_works_particulars')


def format_financial(charge, content):
    if charge.amount_originally_secured:
        content[_('Amount')] = f"£{charge.format_money_field_for_display('amount_originally_secured')}"
        rate_of_interest = charge.format_interest_rate_for_display()
        try:
            float(rate_of_interest)
            rate_of_interest = f"{rate_of_interest}&#37;"
        except ValueError:
            pass
        content[_('Interest rate')] = rate_of_interest


def format_lon(charge, heading, content):
    heading["registration_date"] = charge.format_date_for_display("registration_date")
    if charge.charge_geographic_description:
        content[f"{_('Location')}\n{_('(dominant building)')}"] = \
            charge.charge_geographic_description.splitlines()
    else:
        content[f"{_('Location')}\n{_('(dominant building)')}"] = charge.format_charge_address_for_display()
    for index, applicant in enumerate(charge.format_applicants_for_display()):
        applicant_details = [applicant['applicant_name']]
        applicant_details.extend(applicant['applicant_address'])
        content[_('Applicant %(applicant_no)s details', applicant_no=index + 1)] = applicant_details
    content[_('Interest in land')] = charge.format_field_for_display('servient_land_interest_description')
    content[_('Height of servient land development')] = charge.format_height_pos_for_display('height')
    content[_('Covers all or part of extent')] = charge.format_height_pos_for_display('position')
    if 'temporary-certificate' in charge.documents_filed:
        content[f"{_('Start date')}\n{_('(temporary certificate)')}"] = \
            charge.format_date_for_display('tribunal_temporary_certificate_date')
        content[f"{_('Expiry date')}\n{_('(temporary certificate)')}"] = \
            charge.format_date_for_display('tribunal_temporary_certificate_expiry_date')
    if 'definitive-certificate' in charge.documents_filed:
        content[f"{_('Start date')}\n{_('(definitive certificate)')}"] = \
            charge.format_date_for_display('tribunal_definitive_certificate_date')
        content[f"{_('Expiry date')}\n{_('(definitive certificate)')}"] = \
            charge.format_date_for_display('expiry_date', default=_('Does not expire'))
    content[_('Law')] = charge.format_field_for_display('statutory_provision')
    content[_('Legal document')] = charge.format_field_for_display('instrument')
    content[_('HM Land Registry reference')] = charge.format_llc_ref_for_display('local_land_charge')
