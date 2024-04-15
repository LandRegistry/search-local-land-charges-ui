from datetime import datetime

from flask import current_app, session
from landregistry.exceptions import ApplicationError

from server.dependencies.llc1_document_api.llc1_document_api_service import (
    LLC1DocumentAPIService,
)
from server.dependencies.local_authority_api.local_authority_api_service import (
    LocalAuthorityAPIService,
)
from server.dependencies.report_api.report_api_service import ReportAPIService
from server.dependencies.search_local_land_charge_api.search_local_land_charge_service import (
    SearchLocalLandChargeService,
)
from server.models.searches import PaidSearchItem
from server.services.search_by_area import SearchByArea
from server.services.search_utilities import get_charge_items


class PaidSearchUtils(object):
    @staticmethod
    def request_search_generation(search_extent, address, parent_search_id=None, contact_id=None):
        document_service = LLC1DocumentAPIService(current_app.config)
        llc1_response = document_service.generate(
            search_extent,
            address,
            parent_search_id=parent_search_id,
            contact_id=contact_id,
        )
        return llc1_response.get("search_reference", None)

    @staticmethod
    def pre_associate_search(
        search_ref,
        payment_id,
        search_extent,
        address,
        charges,
        payment_provider,
        card_brand,
        amount,
        reference,
        parent_search_id=None,
    ):
        user_id = session["profile"]["user_id"]

        paid_search = PaidSearchUtils.build_search_item(
            int(search_ref.replace(" ", "")),
            None,
            payment_id,
            search_extent,
            address,
            charges,
            payment_provider,
            card_brand,
            user_id,
            amount,
            reference,
            parent_search_id,
        )

        current_app.logger.info("Pre-associating paid search")
        search_local_land_charge_service = SearchLocalLandChargeService(current_app.config)
        search_local_land_charge_service.save_users_paid_search(user_id, paid_search)

        repeat = False
        if parent_search_id:
            repeat = True

        geometry_collection = {
            "type": "GeometryCollection",
            "geometries": [feature["geometry"] for feature in search_extent["features"]],
        }
        authorities = LocalAuthorityAPIService.get_authorities_by_extent(geometry_collection)

        migrated_authorities = [authority for authority, migrated in authorities.items() if migrated]

        ReportAPIService.send_event(
            "llc1_search",
            {
                "channel": "SEARCH SERVICE",
                "customer": "SEARCH FOR LOCAL LAND CHARGES",
                "charge_authorities": migrated_authorities,
                "charge_count": len(charges) if charges else 0,
                "repeat": repeat,
            },
        )

    @staticmethod
    def get_search_result(
        search_ref,
        payment_id,
        search_extent,
        address,
        charges,
        payment_provider,
        card_brand,
        amount,
        reference,
        parent_search_id=None,
    ):
        document_service = LLC1DocumentAPIService(current_app.config)
        llc1_response = document_service.poll(search_ref)

        if not llc1_response:
            current_app.logger.info("LLC1 generation result not yet available")
            return None

        current_app.logger.info("LLC1 generation succeeded")

        user_id = session["profile"]["user_id"]

        paid_search = PaidSearchUtils.build_search_item(
            int(llc1_response["reference_number"].replace(" ", "")),
            llc1_response["document_url"],
            payment_id,
            search_extent,
            address,
            charges,
            payment_provider,
            card_brand,
            user_id,
            amount,
            reference,
            parent_search_id,
        )

        current_app.logger.info("Saving paid search")
        search_local_land_charge_service = SearchLocalLandChargeService(current_app.config)
        search_local_land_charge_service.save_users_paid_search(user_id, paid_search)

        return paid_search

    @staticmethod
    def search_by_area(extent):
        current_app.logger.info("Calling search api with extent")

        search_by_area_processor = SearchByArea(current_app.logger, current_app.config)
        response = search_by_area_processor.process(extent, results_filter="cancelled")

        if response["status"] == 200:
            current_app.logger.info("Charges found")
            charges = get_charge_items(response.get("data"))
        elif response["status"] == 404:
            current_app.logger.info("No search results found")
            charges = None
        else:
            current_app.logger.error("Failed to search by area, status code {}".format(response["status"]))
            raise ApplicationError("Failed to search by area", "PSEARCH01", 500)

        return charges

    @staticmethod
    def build_search_item(
        search_id,
        document_url,
        payment_id,
        search_extent,
        address,
        charges,
        payment_provider,
        card_brand,
        user_id,
        amount,
        reference,
        parent_search_id=None,
    ):
        paid_search = PaidSearchItem()
        paid_search.search_id = search_id
        paid_search.document_url = document_url
        paid_search.user_id = user_id
        paid_search.payment_id = payment_id
        paid_search.search_date = datetime.now()
        paid_search.search_extent = search_extent
        paid_search.search_area_description = address
        paid_search.charges = charges
        paid_search.lapsed_date = None
        paid_search.payment_provider = payment_provider
        paid_search.card_brand = card_brand
        paid_search.amount = amount
        paid_search.reference = reference

        if parent_search_id:
            paid_search.parent_search_id = parent_search_id

        return paid_search

    @staticmethod
    def format_search_id(search_id):
        padded_id = "{}".format(search_id).zfill(9)
        formatted_id = " ".join(padded_id[i : i + 3] for i in range(0, len(padded_id), 3))
        return formatted_id[:11]
