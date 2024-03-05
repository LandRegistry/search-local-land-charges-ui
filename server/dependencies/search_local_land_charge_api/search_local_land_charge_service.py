from flask import current_app, g
from datetime import datetime
from landregistry.exceptions import ApplicationError
from server.models.searches import PaidSearchItem
from server.dependencies.llc1_document_api.llc1_document_api_service \
    import LLC1DocumentAPIService


class SearchLocalLandChargeService(object):
    """Service class for making requests to /local_land_charges endpoint."""

    def __init__(self, config):
        self.config = config
        self.url = config['SEARCH_LOCAL_LAND_CHARGE_API_URL']

    def save_users_paid_search(self, user_id, paid_search_item):
        current_app.logger.info("Submit paid search save")

        if user_id is None:
            user_id = 'anonymous'

        response = g.requests.post("{}/users/{}/paid-searches".format(self.url, user_id),
                                   json=paid_search_item.to_json(),
                                   headers={'Content-Type': 'application/json'})

        if response.status_code != 201:
            raise ApplicationError('Failed to save paid search item', "SLLC01", 500)

        return response

    def get_paid_search_items(self, user_id):
        url = self.url + '/users/{}/paid-searches'.format(user_id)
        current_app.logger.info("Calling Search Local Land Charge API at {}".format(url))
        response = g.requests.get(url)

        if response.status_code == 404:
            return []
        elif response.status_code != 200:
            raise ApplicationError("Error calling search-local-land-charge-api", "SLLC02", response.status_code)

        searches = PaidSearchItem.from_json_list(response.json())

        return searches

    def get_paid_search_item(self, user_id, search_id):
        url = self.url + '/users/{}/paid-searches/{}'.format(user_id, search_id)
        current_app.logger.info("Calling Search Local Land Charge API at {}".format(url))
        response = g.requests.get(url)

        if response.status_code != 200:
            raise ApplicationError("Error calling search-local-land-charge-api", "SLLC03", response.status_code)

        return PaidSearchItem.from_json(response.json())

    def save_free_search(self, user_id, charge_ids, extent, address):
        current_app.logger.info("Submit free search save")

        if user_id is None:
            user_id = 'anonymous'

        response = g.requests.post("{}/free-searches".format(self.url),
                                   json={"user-id": user_id,
                                         "charge-ids": charge_ids,
                                         "search-extent": extent,
                                         "search-date": datetime.now().isoformat(),
                                         "address": address},
                                   headers={'Content-Type': 'application/json'})

        if response.status_code != 201:
            raise ApplicationError('Failed to save free search item', "SLLC04", 500)

        return response.json()

    def get_free_search(self, search_id):
        current_app.logger.info("Get free search")

        response = g.requests.get(f"{self.url}/free-searches/{search_id}")

        if response.status_code != 200:
            raise ApplicationError('Failed to get free search item', "SLLC05", 500)

        return response.json()

    def get_service_messages(self):
        url = self.url + '/service-messages'
        current_app.logger.info("Calling Search Local Land Charge API at {}".format(url))
        response = g.requests.get(url)

        if response.status_code == 404:
            return []

        if response.status_code != 200:
            raise ApplicationError("Error calling search-local-land-charge-api", "SLLC06", response.status_code)

        display_messages = []

        for message_obj in response.json()["messages"]:
            if g.locale == 'cy':
                message = message_obj.get('message-cy')
                # display links if welsh versions present, otherwise default to English links
                hyperlink_message = message_obj.get('hyperlink-message-cy') or \
                    message_obj.get('hyperlink-link-cy') or \
                    message_obj.get('hyperlink-link-en')
                hyperlink_link = message_obj.get('hyperlink-link-cy') or \
                    message_obj.get('hyperlink-link-en')
            else:
                message = message_obj.get('message-en')
                hyperlink_message = message_obj.get('hyperlink-message-en') or \
                    message_obj.get('hyperlink-link-en')
                hyperlink_link = message_obj.get('hyperlink-link-en')

            display_obj = {'message': message,
                           'link_text': hyperlink_message,
                           'link': hyperlink_link}
            display_messages.append(display_obj)

        return display_messages

    def check_for_completed_doc_url(self, search):
        if not search.document_url:
            current_app.logger.warning(
                "Empty document_url, checking for generated PDF for search {}".format(search.search_id))
            llc1_service = LLC1DocumentAPIService(self.config)
            try:
                llc1_resp = llc1_service.poll(str(search.search_id))
                if llc1_resp:
                    document_url = llc1_resp['document_url']
                else:
                    document_url = None

                if document_url:
                    search.document_url = document_url
                    self.save_users_paid_search(search.user_id, search)

            except ApplicationError as e:
                current_app.logger.exception(
                    "Failed to retrieve PDF information from LLC1, exception: {}".format(str(e)))
                search.document_url = "ERROR"

        return search

    def get_free_search_items(self, user_id, page_size, page):
        url = f'{self.url}/free-searches/user_id/{user_id}'
        current_app.logger.info(f'Calling Search Local Land Charge API at {url}')
        response = g.requests.get(url, params={"page": page, 'per_page': page_size})

        if response.status_code == 404:
            return {}
        elif response.status_code != 200:
            raise ApplicationError("Error calling search-local-land-charge-api", "SLLC07", response.status_code)

        return response.json()

    def get_free_search_for_user_by_search_id(self, user_id, search_id):
        url = f'{self.url}/free-searches/user_id/{user_id}/{search_id}'
        current_app.logger.info(f'Calling Search Local Land Charge API at {url}.')
        response = g.requests.get(url)

        if response.status_code == 404:
            return []
        elif response.status_code != 200:
            raise ApplicationError("Error calling search-local-land-charge-api", "SLLC08", response.status_code)

        return [response.json()]
