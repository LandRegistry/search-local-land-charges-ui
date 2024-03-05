from datetime import datetime
from flask import render_template, Blueprint, request
from server.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityAPIService
from server.services.back_link_history import reset_history
from server.services.datetime_formatter import format_date


originating_authorities = Blueprint(
    "originating_authorities", __name__, template_folder="../templates/originating-authorities"
)


@originating_authorities.route("/originating-authorities", methods=["GET", "POST"])
def originating_authorities_json():
    if request.method == 'POST':
        params = request.json()
    else:
        params = {}
    return LocalAuthorityAPIService.get_organisations(params=params)


@originating_authorities.route("/originating-authorities-list")
def originating_authorities_list():
    reset_history()
    oa_list = LocalAuthorityAPIService.get_organisations(params={})

    return render_template("originating-authorities-list.html", oa_list=oa_list, format_date=format_date,
                           fromisoformat=datetime.fromisoformat)
