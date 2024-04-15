from flask import current_app, session

from server.dependencies.search_local_land_charge_api.search_local_land_charge_service import (
    SearchLocalLandChargeService,
)


def has_free_searches_to_repeat():
    search_llc_service = SearchLocalLandChargeService(current_app.config)
    free_search_results = search_llc_service.get_free_search_items_to_repeat(session["profile"]["user_id"], 1, 1)
    return free_search_results["total"] > 0


def has_paid_searches_to_repeat():
    search_llc_service = SearchLocalLandChargeService(current_app.config)
    paid_search_results = search_llc_service.get_paid_search_items_to_repeat(session["profile"]["user_id"], 1, 1)

    return paid_search_results["total"] > 0
