from flask import Blueprint, current_app, redirect, render_template, session, url_for
from landregistry.exceptions import ApplicationError

from server.dependencies.local_authority_api.local_authority_api_service import (
    LocalAuthorityAPIService,
)
from server.views.forms.check_migrated_authorities_form import (
    CheckMigratedAuthoritiesForm,
)

check_migrated_authorities = Blueprint(
    "check_migrated_authorities",
    __name__,
    template_folder="../templates/check-migrated-authorities",
)


@check_migrated_authorities.route("/check-if-an-authority-is-migrated", methods=["GET"])
def old_check_authorities():
    return redirect(url_for("check_migrated_authorities.check_authorities"))


@check_migrated_authorities.route("/check-if-a-local-authority-is-available-on-this-service", methods=["GET", "POST"])
def check_authorities():
    current_app.logger.info("Check authorities page")
    form = CheckMigratedAuthoritiesForm()
    orgs_choices = [("", "\xa0")]
    org_list = LocalAuthorityAPIService.get_organisations()
    org_name_list = [(organisation["title"], organisation["title"]) for organisation in org_list]
    orgs_choices.extend(org_name_list)
    form.organisation_search.choices = orgs_choices

    if form.validate_on_submit():
        current_app.logger.info("Valid authority, showing result")
        for organisation in org_list:
            if form.organisation_search.data.lower() == organisation["title"].lower():
                session["zoom_to_authority"] = form.organisation_search.data
                session["organisation_details"] = organisation
                return redirect(url_for("check_migrated_authorities.show_authority_migrated_details"))
        # Should never happen
        raise ApplicationError("Unable to find selected authority", "LAUTH01", 500)

    return render_template("check-migrated-authorities.html", form=form)


@check_migrated_authorities.route("/authority-migrated-details", methods=["GET"])
def show_authority_migrated_details():
    current_app.logger.info("Show authority migrated details page")
    organisation = session["organisation_details"]

    return render_template(
        "show-migrated-authority.html",
        org_name=organisation["title"],
        migrated=organisation["migrated"],
        maintenance=organisation["maintenance"],
    )
