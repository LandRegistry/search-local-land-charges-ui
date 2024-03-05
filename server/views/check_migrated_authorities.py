from flask import render_template, current_app, Blueprint, session
from flask_babel import lazy_gettext as _
from server.views.forms.check_migrated_authorities_form import CheckMigratedAuthoritiesForm
from server.dependencies.local_authority_api.local_authority_api_service import LocalAuthorityAPIService
from landregistry.exceptions import ApplicationError

check_migrated_authorities = Blueprint("check_migrated_authorities", __name__,
                                       template_folder="../templates/check-migrated-authorities")


@check_migrated_authorities.route("/check-if-an-authority-is-migrated", methods=["GET", "POST"])
def check_authorities():
    current_app.logger.info("Check authorities page")
    form = CheckMigratedAuthoritiesForm()
    orgs_choices = [("", _("Select authority name"))]
    org_list = LocalAuthorityAPIService.get_organisations()
    org_name_list = [(organisation['title'], organisation['title']) for organisation in org_list]
    orgs_choices.extend(org_name_list)
    form.organisation_search.choices = orgs_choices

    if form.validate_on_submit():
        current_app.logger.info("Valid authority, showing result")
        for organisation in org_list:
            if form.organisation_search.data.lower() == organisation['title'].lower():
                migrated = organisation['migrated']
                maintenance = organisation['maintenance']
                session['zoom_to_authority'] = form.organisation_search.data
                return render_template('check-migrated-authorities.html', form=form, migrated=migrated,
                                       maintenance=maintenance)
        # Should never happen
        raise ApplicationError("Unable to find selected authority", "LAUTH01", 500)

    return render_template('check-migrated-authorities.html', form=form)
