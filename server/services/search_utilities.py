import math
from flask import current_app, session, url_for
from server.models.searches import SearchState
from server.dependencies.search_local_land_charge_api.search_local_land_charge_service \
    import SearchLocalLandChargeService
from cryptography.fernet import Fernet
from flask_babel import gettext as _

from server.services.back_link_history import reset_history


def start_new_search():
    session['search_state'] = SearchState()
    session.pop('payment_state', None)
    session.pop('unmerged_extent', None)
    session.pop('address_search_term', None)
    session.pop('address_search_results', None)
    session.pop('zoom_to_location', None)
    session.pop('coordinate_search', None)
    reset_history()


def decode_validate_search_id(enc_search_id):

    f = Fernet(current_app.config['GEOSERVER_SECRET_KEY'])
    search_id = f.decrypt(enc_search_id).decode()
    sllc_service = SearchLocalLandChargeService(current_app.config)
    free_search = sllc_service.get_free_search(search_id)
    if free_search.get('user-id') != session['profile']['user_id']:
        return None
    search_state = SearchState()
    search_state.address = free_search.get('address', None)
    search_state.free_search_id = free_search.get('id', None)
    search_state.search_extent = free_search.get('search-extent', None)

    return search_state


def get_charge_items(results):
    charges = []

    for result in results:
        result['item'].update({'adjoining': result.get('adjoining', False)})
        charges.append(result['item'])

    return charges


def calculate_pagination_info(items, paginate_url, items_per_page, current_page, paginate_args=None,
                              no_of_pages=None, no_of_items=None):
    if paginate_args is None:
        paginate_args = {}
    if no_of_items is None:
        no_of_items = len(items)
    if no_of_pages is None:
        no_of_pages = int(math.ceil(no_of_items / items_per_page))

    # This works out the index of the first address on this page
    start_index = items_per_page * (current_page - 1)

    # This works out the index of the last address on this page
    end_index = (
        no_of_items - 1 if current_page == no_of_pages
        else (items_per_page * current_page) - 1)

    pagination_info = {'items': []}

    if current_page > 1:
        pagination_info['previous'] = {
            "href": url_for(paginate_url, page=current_page - 1, **paginate_args),
            "text": _("Previous"),
        }
        if current_page > 2:
            pagination_info['items'].append({
                "number": 1,
                "href": url_for(paginate_url, **paginate_args)
            })
        if current_page > 3:
            pagination_info['items'].append({
                "ellipsis": True
            })
        pagination_info['items'].append({
            "number": current_page - 1,
            "href": url_for(paginate_url, page=current_page - 1, **paginate_args)
        })
    pagination_info['items'].append({
        "number": current_page,
        "href": url_for(paginate_url, page=current_page, **paginate_args),
        "current": True
    })
    if current_page < no_of_pages:
        pagination_info["items"].append({
            "number": current_page + 1,
            "href": url_for(paginate_url, page=current_page + 1, **paginate_args)
        })
        if current_page < no_of_pages - 2:
            pagination_info['items'].append({
                "ellipsis": True
            })
        if current_page < no_of_pages - 1:
            pagination_info["items"].append({
                "number": no_of_pages,
                "href": url_for(paginate_url, page=no_of_pages, **paginate_args)
            })
        pagination_info['next'] = {
            "href": url_for(paginate_url, page=current_page + 1, **paginate_args),
            "text": _('Next'),
        }

    display_items = None
    if items is not None:
        # slice the items list to only have the content required on the page
        display_items = items[start_index:end_index + 1]

    return display_items, pagination_info, start_index
