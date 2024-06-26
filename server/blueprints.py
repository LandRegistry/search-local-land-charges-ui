# Import every blueprint file
from server.views import (
    account_admin,
    ajax,
    auth,
    categories_stat_provs,
    check_migrated_authorities,
    index,
    language,
    main,
    my_account,
    originating_authorities,
    paid_search,
    search,
    search_results,
    sign_in,
)


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(index.index)
    app.register_blueprint(main.main)
    app.register_blueprint(language.language)
    app.register_blueprint(auth.auth)
    app.register_blueprint(sign_in.sign_in)
    app.register_blueprint(check_migrated_authorities.check_migrated_authorities)
    app.register_blueprint(search.search)
    app.register_blueprint(ajax.ajax)
    app.register_blueprint(search_results.search_results)
    app.register_blueprint(paid_search.paid_search)
    app.register_blueprint(my_account.my_account)
    app.register_blueprint(account_admin.account_admin)
    app.register_blueprint(categories_stat_provs.categories_stat_provs)
    app.register_blueprint(originating_authorities.originating_authorities)

    # All done!
    app.logger.info("Blueprints registered")
