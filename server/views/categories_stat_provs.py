import json
from datetime import datetime

from flask import Blueprint, Response, current_app, render_template, request
from landregistry.exceptions import ApplicationError

from server.dependencies.maintain_api.category_service import CategoryService
from server.dependencies.maintain_api.statutory_provisions_service import (
    StatProvService,
)
from server.services.back_link_history import reset_history, show_back_link
from server.services.datetime_formatter import format_date

categories_stat_provs = Blueprint(
    "categories_stat_provs",
    __name__,
    template_folder="../templates/categories-stat-provs",
)


@categories_stat_provs.route("/category-list")
def get_page_categories():
    reset_history()
    categories = CategoryService(current_app.config).get_all_and_sub()
    return render_template("category-list.html", categories=categories)


@categories_stat_provs.route("/categories/all")
def get_categories_and_sub():
    categories = CategoryService(current_app.config).get_all_and_sub()
    return Response(response=json.dumps(categories), mimetype="application/json")


@categories_stat_provs.route("/categories")
def get_all_categories():
    categories = CategoryService(current_app.config).get()
    return Response(response=json.dumps(categories), mimetype="application/json")


@categories_stat_provs.route("/categories/<path:category>")
def get_category(category):
    category_info = CategoryService(current_app.config).get_category(category)
    return Response(
        response=json.dumps(category_info.json()),
        mimetype="application/json",
        status=category_info.status_code,
    )


@categories_stat_provs.route("/categories/<path:category>/sub-category/<path:sub_category>")
def get_sub_category(category, sub_category):
    sub_category_info = CategoryService(current_app.config).get_sub_category(category, sub_category)
    return Response(
        response=json.dumps(sub_category_info.json()),
        mimetype="application/json",
        status=sub_category_info.status_code,
    )


@categories_stat_provs.route("/statutory-provision-list")
def get_page_stat_prov():
    if not show_back_link():
        reset_history()
    sort_by = request.args.get("sort_stat_provs", "title")
    if sort_by not in ["title", "last_updated"]:
        raise ApplicationError("Invalid sort by", "INVSRT01", 400)
    stat_provs_list = format_stat_prov_list(True)
    if sort_by == "last_updated":
        stat_provs_list.sort(
            key=lambda x: x.get("last_updated", datetime.fromisoformat("1900-01-01")),
            reverse=True,
        )
    else:
        stat_provs_list.sort(key=lambda x: x.get("title").upper())
    return render_template(
        "statutory-provision-list.html",
        sort_by=sort_by,
        stat_provs_list=stat_provs_list,
        format_timestamp=format_date,
    )


@categories_stat_provs.route("/statutory-provision-removed-list")
def get_page_stat_prov_removed():
    if not show_back_link():
        reset_history()
    sort_by = request.args.get("sort_stat_provs", "title")
    if sort_by not in ["title", "date_removed"]:
        raise ApplicationError("Invalid sort by", "INVSRT01", 400)
    stat_provs_list = format_stat_prov_list(False)
    stat_provs_list.sort(key=lambda x: x.get("title").upper())
    if sort_by == "date_removed":
        stat_provs_list.sort(
            key=lambda x: x.get("last_updated", datetime.fromisoformat("1900-01-01")),
            reverse=True,
        )
    return render_template(
        "statutory-provision-removed-list.html",
        sort_by=sort_by,
        stat_provs_list=stat_provs_list,
        format_timestamp=format_date,
    )


@categories_stat_provs.route("/statutory-provisions")
def get_json_stat_prov():
    selectable = request.args.get("selectable", "TRUE")
    stat_provs = StatProvService(current_app.config).get(selectable)
    return Response(response=json.dumps(stat_provs), mimetype="application/json")


@categories_stat_provs.route("/statutory-provisions/history")
def get_json_stat_prov_history():
    stat_provs = StatProvService(current_app.config).get_history()
    return Response(response=json.dumps(stat_provs), mimetype="application/json")


def format_stat_prov_list(selectable):
    stat_provs = StatProvService(current_app.config).get_history()
    stat_provs_dict = {}
    for stat_prov in stat_provs:
        if stat_prov["display_title"] not in stat_provs_dict:
            stat_provs_dict[stat_prov["display_title"]] = {
                "title": stat_prov["display_title"],
                "previous_titles": [],
                "selectable": False,
            }
        if stat_prov["display_title"] != stat_prov["title"]:
            stat_provs_dict[stat_prov["display_title"]]["previous_titles"].append(stat_prov["title"])
        last_updated = stat_prov.get("unselectable_timestamp", None)
        if not last_updated and stat_prov["selectable"]:
            last_updated = stat_prov.get("created_timestamp", None)
        current_last_updated = stat_provs_dict[stat_prov["display_title"]].get("last_updated", None)
        if (current_last_updated and last_updated) or (last_updated and not current_last_updated):
            last_updated_date = datetime.fromisoformat(last_updated)
            if not current_last_updated or last_updated_date > current_last_updated:
                stat_provs_dict[stat_prov["display_title"]]["last_updated"] = last_updated_date
        if stat_prov["selectable"]:
            stat_provs_dict[stat_prov["display_title"]]["selectable"] = True
    return [prov for prov in stat_provs_dict.values() if prov["selectable"] == selectable]
