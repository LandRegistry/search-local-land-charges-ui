from deepmerge import Merger


class WTFormsHelpersGroups(object):
    """WTForms helpers which supports group errors

    Register some template helpers to allow developers to
    map WTForms elements to the GOV.UK jinja macros
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.add_template_global(wtforms_errors)


def wtforms_errors(form, params=None):
    if not params:
        params = {}
    wtforms_params = {"titleText": "There is a problem", "errorList": []}

    wtforms_params["errorList"] = flatten_errors(form.errors)

    return merger.merge(wtforms_params, params)


def flatten_errors(errors, prefix=""):
    """Return list of errors from form errors."""
    error_list = []
    if isinstance(errors, dict):
        # if the error dict has a first_child_name, override prefix so first child is used in summary link
        if "first_child_name" in errors.keys():
            error_prefix = errors.pop("first_child_name")
        else:
            error_prefix = None
        for key, value in errors.items():
            # Recurse to handle subforms.
            if not error_prefix:
                sub_prefix = f"{prefix}{key}-"
            else:
                sub_prefix = error_prefix
            error_list += flatten_errors(value, prefix=sub_prefix)
    elif isinstance(errors, list) and isinstance(errors[0], dict):
        for idx, error in enumerate(errors):
            error_list += flatten_errors(error, prefix=f"{prefix}{idx}-")
    elif isinstance(errors, list):
        error_list.append({"text": errors[0], "href": "#{}".format(prefix.rstrip("-"))})
    else:
        error_list.append({"text": errors, "href": "#{}".format(prefix.rstrip("-"))})
    return error_list


merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [(list, ["append"]), (dict, ["merge"])],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"],
)

wtforms_helpers = WTFormsHelpersGroups()
