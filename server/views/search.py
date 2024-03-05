import json
from flask import render_template, current_app, Blueprint, flash, session, request
from server.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityAPIService
from server.dependencies.search_local_land_charge_api.search_local_land_charge_service \
    import SearchLocalLandChargeService
from server.dependencies.search_api.address_service import AddressesService
from server.dependencies.search_api.search_type import SearchType
from server.models.charges import LocalLandChargeItem
from server.models.searches import SearchState
from server.services.search_by_text import SearchByText
from server.services.search_by_inspire_id import SearchByInspireId
from server.services.search_by_charge_id import SearchByChargeId
from server.services.merge_polygons import merge_polygons
from server.views.auth import authenticated
from server.views.forms.confirm_search_area_form import ConfirmSearchAreaForm
from server.views.forms.define_search_area_form import DefineSearchAreaForm
from server.views.forms.search_by_inspire_id_form import SearchByInspireIDForm
from server.views.forms.search_postcode_address_form import SearchPostcodeAddressForm
from server.views.forms.search_by_coordinates_form import SearchByCoordinatesForm
from server.views.forms.search_by_title_number_form import SearchByTitleNumberForm
from server.services.check_migration_status import CheckMigrationStatus
from server.services.search_by_uprn import SearchByUprn
from server.services.search_by_usrn import SearchByUsrn
from server.services.search_by_area import SearchByArea
from server.dependencies.audit_api.audit_api_service import AuditAPIService
from server.dependencies.report_api.report_api_service import ReportAPIService
from server.services.check_maintenance_status import CheckMaintenanceStatus
from flask import redirect, url_for
from server.services.search_utilities import calculate_pagination_info, start_new_search
from flask_babel import lazy_gettext as _
from landregistry.exceptions import ApplicationError

search = Blueprint("search", __name__, url_prefix="/search", template_folder="../templates/search")

ADDRESSES_PER_PAGE = 20


@search.route("/search-by-postcode-address", methods=["GET", "POST"])
@authenticated
def search_by_post_code_address():
    start_new_search()

    current_app.logger.info("Search postcode address page")

    form = SearchPostcodeAddressForm()

    if form.validate_on_submit():
        current_app.logger.info("Valid search term")

        search_term = form.search_term.data.strip()

        search_by_text_processor = SearchByText(current_app.logger)
        response = search_by_text_processor.process(search_term, current_app.config)
        search_results = response.get("data")
        # only return search results that are properties or streets, this should cover all types but filter just in case
        properties = [address for address in search_results if address.get('address_type') in ['property', 'street']]
        search_status = response.get("status")

        if search_status == "success" and len(properties) > 0:
            session['address_search_results'] = properties
            session['address_search_term'] = search_term
            return redirect(url_for('search.address_search_results'))

        form.search_term.errors.append(_('No results found'))

    service_messages = SearchLocalLandChargeService(current_app.config).get_service_messages()
    if service_messages:
        flash(service_messages, "service_message")

    return render_template('search-post-code-address.html', form=form)


@search.route("/address-search-results")
@authenticated
def address_search_results():
    current_app.logger.info("Search address search results page")
    if "search_state" not in session:
        return redirect(url_for('index.index_page'))
    if "address_search_results" not in session:
        return redirect(url_for('search.search_by_post_code_address'))

    addresses = session['address_search_results']
    display_page = request.args.get("page", 1, type=int)

    display_addresses, pagination_info, start_index = \
        calculate_pagination_info(addresses, 'search.address_search_results', ADDRESSES_PER_PAGE, display_page)

    return render_template('address-search-results.html',
                           addresses=display_addresses,
                           search_term=session['address_search_term'],
                           no_of_addresses=len(addresses),
                           show_pagination=len(addresses) > ADDRESSES_PER_PAGE,
                           start_index=start_index,
                           pagination_info=pagination_info
                           )


@search.route("/address-details")
@authenticated
def address_details():
    current_app.logger.info('Loading address details page')

    if 'search_state' not in session:
        return redirect(url_for('index.index_page'))
    if "address_search_results" not in session:
        return redirect(url_for('search.search_by_post_code_address'))

    index = request.args.get("index", 0, type=int)
    address_selected = session['address_search_results'][index]
    session['search_state'].address = address_selected.get('address')
    # clear previous extent data in case an index mapped address was previously selected and then this page was
    # returned to with the back button
    session.pop('unmerged_extent', None)
    session['search_state'].search_extent = None
    session.modified = True

    if address_selected.get('address_type') == 'property':
        return property_address_selected(address_selected)
    else:
        return street_address_selected(address_selected)


def property_address_selected(address_selected):
    # If the user selected a property, do a UPRN search to get the property details
    if address_selected.get('uprn'):
        uprn = str(address_selected.get('uprn'))
        search_by_uprn_processor = SearchByUprn(current_app.logger)
        response = search_by_uprn_processor.process(uprn, current_app.config, True)
        search_results = response.get("data")

        # get all features from each entry returned by index map api. There will probably always only be one,
        # but do the loop just in case
        features = []

        for address in search_results:
            index_map = address.get('index_map')
            if index_map:
                features += index_map.get('features')

        if features:
            all_features = {"type": "FeatureCollection",
                            "features": features}

            merged_extent = merge_polygons(all_features)

            migration_status = CheckMigrationStatus.process(merged_extent)

            if not migration_status:
                raise ApplicationError("Failed to check authority intersection migration status", "MIGSTAT01", 500)

            if migration_status['flag'] != "pass" and migration_status['includes_migrated']:
                current_app.logger.warning("index map extent partially migrated, go to draw search area")
            else:
                # add these so map zoom will work
                session['unmerged_extent'] = all_features
                session['search_state'].search_extent = merged_extent

                return redirect(url_for('search.confirm_search_area'))

    # If no UPRN or location data, default to the define search area screen with "Draw a search area" text
    geometry = address_selected.get('geometry')
    if geometry:
        # Because a property was selected, the geometry will be a point that represents the location
        session['zoom_to_location'] = [geometry.get('coordinates')]
    return redirect(url_for('search.define_search_area', page_style="draw"))


def street_address_selected(address_selected):
    # Otherwise, it was a street selected, so search for the area using the USRN
    if address_selected.get('usrn'):
        usrn = str(address_selected.get('usrn'))
        postcode = address_selected.get('postcode')
        search_by_usrn_processor = SearchByUsrn(current_app.logger)
        response = search_by_usrn_processor.process(usrn, postcode, current_app.config)
        search_results = response.get("data")

        # only return search results that are properties or streets, this should cover all types but filter just
        # in case
        properties = [address for address in search_results if
                      address.get('address_type') in ['property', 'street']]
        search_status = response.get("status")

        if search_status == "success" and len(properties) > 0:
            geometry = address_selected.get('geometry')
            if geometry:
                # set the zoom to location in case they click the link to the map screen before selecting a
                # property
                session['zoom_to_location'] = geometry.get('coordinates')

            session['address_search_results'] = properties
            session['address_search_term'] = address_selected.get('address')

            return redirect(url_for('search.address_search_results'))

    # If no USRN or properties found for the street, default to the define search area screen with
    # "Draw a search area" text
    geometry = address_selected.get('geometry')
    if geometry:
        # Because a street was selected, the geometry will be a line that represents the location
        session['zoom_to_location'] = geometry.get('coordinates')
    return redirect(url_for('search.define_search_area', page_style="draw"))


@search.route("/search-by-coordinates", methods=["GET", "POST"])
@authenticated
def search_by_coordinates():
    current_app.logger.info('Coordinate search page')
    start_new_search()

    form = SearchByCoordinatesForm()

    if form.validate_on_submit():
        current_app.logger.info("Valid search coordinates")

        session['coordinate_search'] = True
        session['zoom_to_location'] = [float(form.eastings.data), float(form.northings.data)]

        return redirect(url_for('search.define_search_area', page_style="draw"))

    return render_template('search-by-coordinates.html', form=form)


@search.route("/search-by-title-number", methods=["GET", "POST"])
@authenticated
def search_by_title_number():
    current_app.logger.info('Title number search page')
    start_new_search()

    form = SearchByTitleNumberForm()

    if form.validate_on_submit():
        current_app.logger.info("Valid title number")

        current_app.logger.info('Calling search api')
        addresses_service = AddressesService(current_app.config)
        response = addresses_service.get_by(SearchType.TITLE.value, form.title_number.data.strip())

        if response.status_code == 200:
            current_app.logger.info("Index geometry found")
            index_map = response.json()
            merged_extent = merge_polygons(index_map)
            # add these so map zoom will work
            session['unmerged_extent'] = index_map
            session['search_state'].search_extent = merged_extent

            return redirect(url_for('search.confirm_search_area'))
        elif response.status_code in [400, 404]:
            form.title_number.errors.append(
                _('We do not recognise that title number. Check title number and try again'))
        else:
            raise ApplicationError(f"Failed to retrieve search information for title {form.title_number.data.strip()}",
                                   "FTITLE01", 500)

    return render_template('search-by-title-number.html', form=form)


@search.route("/search-by-inspire-id", methods=["GET", "POST"])
@authenticated
def search_by_inspire_id():
    current_app.logger.info('Inspire search page')

    start_new_search()

    form = SearchByInspireIDForm()

    if form.validate_on_submit():
        current_app.logger.info("Valid inspire id")
        current_app.logger.info('Calling inspire api')
        search_by_inspire_processor = SearchByInspireId(current_app.logger, current_app.config)
        response_inspire_search = search_by_inspire_processor.process(form.inspire_id.data)

        if response_inspire_search.get('status') == 200:
            current_app.logger.info("Charge found")
            charge_data = response_inspire_search.get('data')
            charge_id = charge_data.get('llc_id')
            search_by_charge_id_processor = SearchByChargeId(current_app.logger)
            response_charge_search = search_by_charge_id_processor.process(charge_id, current_app.config)
            if response_charge_search.get('status') == 'success':
                # add the charge to the session, although this is an array there will only ever be one result
                session['search_state'].charges = response_charge_search.get('data')
                session.modified = True
                return redirect(url_for('search.inspire_search_results'))
            else:
                # this means the search for charge ID has failed, which should never happen as we are getting the charge
                # ID from the inspire database so it should always be correct, but handle it just in case
                form.inspire_id.errors.append(response_charge_search.get('search_message'))

        elif response_inspire_search.get('status') in [400, 404]:
            form.inspire_id.errors.append(_('You have entered an invalid INSPIRE ID'))
        else:
            current_app.logger.error("Failed to search by area, status code {}"
                                     .format(response_inspire_search.get('status')))
            raise ApplicationError("Failed to search by area", "SRCHA01", 500)

    return render_template('search-by-inspire-id.html', form=form)


@search.route("/search-by-inspire-id/results")
@authenticated
def inspire_search_results():
    current_app.logger.info('Loading inspire results page')

    if "search_state" not in session or not session['search_state'].charges:
        return redirect(url_for('index.index_page'))

    # because we searched by inspire ID, there'll only be one charge in the list so use it
    charge_data = session['search_state'].charges[0]
    charge_extent = charge_data.get('geometry')
    charge = charge_data.get('item')
    charge_obj = LocalLandChargeItem.from_json(charge)

    return render_template('results-from-inspire-search.html',
                           back_link=True,
                           charge=charge_obj,
                           geometry=json.dumps(charge_extent))


@search.route("/confirm-search-area", methods=["GET", "POST"])
@authenticated
def confirm_search_area():
    current_app.logger.info('Confirm search area page')

    if 'search_state' not in session:
        return redirect(url_for('index.index_page'))

    form = ConfirmSearchAreaForm()

    authority_data = CheckMigrationStatus.process(session['search_state'].search_extent)

    if not authority_data:
        raise ApplicationError("Failed to check authority intersection migration status", "MIG01", 500)

    if form.validate_on_submit():

        if authority_data['flag'] == "pass":
            # boundaries are inside buffer of migrated authorities
            return search_by_area(session['search_state'].search_extent, session['search_state'].address)
        elif authority_data['flag'] == "warning":
            # boundaries are within buffer zone of non-migrated authorities
            return search_by_area(session['search_state'].search_extent, session['search_state'].address, warning=True)
        else:
            # boundaries exceed buffer zone into a non-migrated authority
            current_app.logger.warning("Drawn polygon intersects with non-migrated authority")
            session['authority_data'] = authority_data

            return redirect((url_for('search.no_information_available')))

    if authority_data['flag'] == "pass":
        # boundaries are inside buffer of migrated authorities
        warning = False
    elif authority_data['flag'] == "warning":
        # boundaries are within buffer zone of non-migrated authorities
        warning = True
    else:
        # boundaries exceed buffer zone into a non-migrated authority
        current_app.logger.warning("Drawn polygon intersects with non-migrated authority")
        session['authority_data'] = authority_data

        return redirect((url_for('search.no_information_available')))

    return render_template('confirm-search-area.html',
                           geometry=json.dumps(session['search_state'].search_extent),
                           maintenance=False,
                           warning=warning,
                           form=form)


def search_by_area(extent, address, warning=False):
    current_app.logger.info('Calling search api with extent {}'.format(extent))
    session['search_state'] = SearchState()

    search_by_area_processor = SearchByArea(current_app.logger, current_app.config)
    response = search_by_area_processor.process(extent, results_filter='cancelled')

    number_of_charges = 0

    if response['status'] == 200:
        current_app.logger.info("Charges found")
        session['search_state'].charges = get_charge_items(response.get('data'))
        if session['search_state'].charges:
            number_of_charges = len(session['search_state'].charges)

    elif response['status'] == 404:
        current_app.logger.info("No search results found")

    elif response['status'] == 507:
        current_app.logger.info("Too many results returned")
        session['search_state'].search_extent = extent
        session['search_state'].address = address

        return render_template('define-search-area.html',
                               style='edit',
                               form=DefineSearchAreaForm(),
                               too_many_results=True,
                               information=json.dumps(session['unmerged_extent']),
                               zoom_extent=json.dumps(extent),
                               maintenance=CheckMaintenanceStatus.under_maintenance())

    else:
        current_app.logger.error("Failed to search by area, status code {}".format(response['status']))
        raise ApplicationError(500)

    session['search_state'].search_extent = extent
    session['search_state'].address = address
    session['warning'] = warning

    AuditAPIService.audit_event("Free Search Performed")

    # Send report information on personal search
    geometry_collection = {"type": "GeometryCollection",
                           "geometries": [feature['geometry'] for feature in extent['features']]}
    authorities = LocalAuthorityAPIService.get_authorities_by_extent(geometry_collection)

    migrated_authorities = [authority for authority, migrated in authorities.items() if migrated]

    ReportAPIService.send_event("personal_search", {
        "charge_authorities": migrated_authorities,
        "charge_count": number_of_charges,
    })

    # Send free search info to api for auditing
    user_id = session['profile']['user_id']
    if session['search_state'].charges:
        charge_ids = [charge['local-land-charge'] for charge in session['search_state'].charges]
    else:
        charge_ids = []
    free_search = SearchLocalLandChargeService(current_app.config).save_free_search(user_id, charge_ids, extent,
                                                                                    address)
    session['search_state'].free_search_id = free_search['id']

    return redirect(url_for('search_results.results'))


def get_charge_items(results):
    charges = []

    for result in results:
        result['item'].update({'adjoining': result.get('adjoining', False)})
        charges.append(result['item'])

    return charges


@search.route("/no-information-available")
@authenticated
def no_information_available():
    if "search_state" not in session or "authority_data" not in session:
        return redirect(url_for('index.index_page'))

    scotland = session['authority_data']['flag'] == "fail_scotland"
    maintenance = session['authority_data']['flag'] == "fail_maintenance"
    maintenance_contact = session['authority_data']['flag'] == "fail_maintenance_contact"
    no_authority = session['authority_data']['flag'] == "fail_no_authority"

    if maintenance or maintenance_contact:
        authority_list = session['authority_data']['plus_buffer']['maintenance_list']
    else:
        authority_list = session['authority_data']['plus_buffer']['non_migrated_list']

    if scotland:
        authority_list.append('Scotland')
    authority_list.sort()

    return render_template(
        'no-information-available.html',
        show_amend_search=len(session['authority_data']['migrated_list']) > 0,
        authorities=authority_list,
        scotland=scotland,
        maintenance=maintenance,
        maintenance_contact=maintenance_contact,
        no_authority=no_authority
    )


@search.route('/<any("find", "edit", "draw"):page_style>-search-area', methods=["GET", "POST"])
@authenticated
def define_search_area(page_style):
    if "search_state" not in session:
        return redirect(url_for('index.index_page'))

    form = DefineSearchAreaForm()

    if form.validate_on_submit():
        current_app.logger.info(form.saved_features.data.strip())
        extent = json.loads(form.saved_features.data.strip())
        merged_extent = merge_polygons(extent)
        session['unmerged_extent'] = extent
        session['search_state'].search_extent = merged_extent

        authority_data = CheckMigrationStatus.process(merged_extent)
        intersection_status = authority_data['flag']

        if intersection_status == "pass":
            # boundaries are inside buffer of migrated authorities
            return search_by_area(merged_extent, session['search_state'].address)
        elif intersection_status == "warning":
            # boundaries are within buffer zone of non-migrated authorities
            return search_by_area(merged_extent, session['search_state'].address, warning=True)
        else:
            # boundaries exceed buffer zone into a non-migrated authority
            current_app.logger.warning("Drawn polygon intersects with non-migrated authority")
            session['authority_data'] = authority_data
            return redirect((url_for('search.no_information_available')))

    search_extent = None
    zoom_extent = None
    zoom_to_location = None
    local_authority_boundary_url = None

    if "unmerged_extent" in session:
        search_extent = json.dumps(session['unmerged_extent'])
        zoom_extent = json.dumps(session['search_state'].search_extent)

    if 'zoom_to_location' in session:
        zoom_to_location = session['zoom_to_location']

    coordinate_search = session.get('coordinate_search', None)

    # Clear the repeated search flag so that the repeated search message is not displayed if a search has
    # previously been repeated
    session.pop('repeated_search', None)

    zoom_to_authority = session.pop('zoom_to_authority', None)
    if zoom_to_authority:
        local_authority_boundary_url = url_for('ajax.local_authority_service_boundingbox', authority=zoom_to_authority)

    return render_template('define-search-area.html',
                           form=form,
                           style=page_style,
                           information=search_extent,
                           coordinate_search=coordinate_search,
                           zoom_extent=zoom_extent,
                           local_authority_boundary_url=local_authority_boundary_url,
                           zoom_to_location=json.dumps(zoom_to_location),
                           maintenance=CheckMaintenanceStatus.under_maintenance())


@search.route("/too-many-results")
@authenticated
def too_many_results():
    return render_template("too-many-results.html")
