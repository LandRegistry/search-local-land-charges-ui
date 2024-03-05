import json
from flask import Blueprint, Response, current_app, request, session
from server.dependencies.llc1_document_api.llc1_document_api_service import LLC1DocumentAPIService
from server.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityAPIService
from server.views.auth import authenticated
from landregistry.exceptions import ApplicationError

ajax = Blueprint("ajax", __name__)


@authenticated
@ajax.route('/_authorities/<authority>/boundingbox', methods=['GET'])
def local_authority_service_boundingbox(authority):
    # AJAX local authority API boundary lookup
    current_app.logger.info("Local Authority bounding box requested")
    if not request.is_xhr:
        raise ApplicationError("Request not xhr", "XHR01", 500)

    response = LocalAuthorityAPIService.get_bounding_box(authority)

    return Response(json.dumps(response.json())), response.status_code, {"Content-Type": "application/json"}


@ajax.route("/paid-search/<enc_search_id>/_llc1_pdf_poll")
@authenticated
def ajax_llc1_pdf_poll(enc_search_id):
    current_app.logger.info('AJAX pdf polling endpoint called')

    if not request.is_xhr:
        raise ApplicationError("Poll request not xhr", "NXHR01", 500)

    search_session = session['paid_searches'][enc_search_id]

    if "search_state" not in search_session or not search_session['search_state'].search_reference:
        return Response(json.dumps({"status": "search reference not set"}), mimetype='application/json', status=404)

    document_service = LLC1DocumentAPIService(current_app.config)
    response = document_service.poll(search_session['search_state'].search_reference)

    if not response:
        return Response(json.dumps({"status": "generating"}), mimetype='application/json', status=202)

    return Response(json.dumps({"status": "success"}), mimetype='application/json', status=201)
