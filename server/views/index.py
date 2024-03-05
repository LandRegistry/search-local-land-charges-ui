from flask import Blueprint, render_template, redirect, current_app, g
from server import config
from server.services.back_link_history import clear_history

# This is the blueprint object that gets registered into the app in blueprints.py.
index = Blueprint("index", __name__)


if config.HOME_PAGE_EN_URL == '/dummy-english' and config.HOME_PAGE_CY_URL == '/dummy-welsh':
    @index.route("/dummy-<any(english, welsh):language>")
    def dummy_gds_index_page(language):
        clear_history()
        current_app.logger.info("Rendering dummy homepage")
        return render_template("index.html", language=language)


@index.route("/")
def index_page():
    clear_history()
    if g.locale == 'cy':
        return redirect(current_app.config['HOME_PAGE_CY_URL'])
    else:
        return redirect(current_app.config['HOME_PAGE_EN_URL'])
