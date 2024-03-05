from flask import current_app, g
from landregistry.exceptions import ApplicationError


class LLC1DocumentAPIService(object):
    """Service class for making requests to /search/addresses endpoint."""
    def __init__(self, config):
        self.config = config
        self.url = config['LLC1_API_URL']

    # Call the LLC1 Document api using given description and extents.
    def generate(self, extents, address, parent_search_id=None, contact_id=None):

        payload = {
            'description': address,
            'extents': extents,
            'source': 'SEARCH',
            'contact_id': contact_id,
            'language': g.locale
        }

        if parent_search_id is not None:
            payload["parent_search_id"] = parent_search_id

        current_app.logger.info("Submit LLC1 search request")
        response = g.requests.post(self.url + '/generate_async',
                                   json=payload,
                                   headers={'Content-Type': 'application/json'})

        if response.status_code != 202:
            current_app.logger.warning('Failed to create LLC1')
            raise ApplicationError('Failed to create LLC1', "LLC101", 500)

        return response.json()

    # Call the LLC1 Document api and poll for completed pdf
    def poll(self, search_ref):

        current_app.logger.info("Submit LLC1 search request")
        response = g.requests.get(self.url + '/poll_llc1/' + search_ref,
                                  headers={'Content-Type': 'application/json'})

        if response.status_code == 202:
            current_app.logger.info('PDF not yet available')
            return None
        elif response.status_code == 201:
            current_app.logger.info('PDF generated')
            return response.json()
        else:
            current_app.logger.warning('Failed to create LLC1, response: {}'.format(response.text))
            raise ApplicationError('Failed to create LLC1', "LLC102", 500)
