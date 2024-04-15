from flask import session, url_for


def add_history(add_url):
    # Ignore history when we're handling a back link
    if "back_link" not in session or not session["back_link"]:
        if "history" in session and len(session["history"]) > 0:
            # Try and handle smart people using both the back links and back button on browser
            # If URL already in history, then slice off anything after that URL
            if add_url in session["history"]:
                url_index = session["history"].index(add_url)
                session["history"] = session["history"][0 : url_index + 1]
            else:
                session["history"].append(add_url)
                session.modified = True
        else:
            session["history"] = [add_url]
    else:
        session["back_link"] = False


def show_back_link():
    return "history" in session and len(session["history"]) > 0


def get_back_url():
    # Flag that we're doing a back link so we need to ignore for history purposes
    session["back_link"] = True
    if "history" in session and len(session["history"]) > 0:
        back_url = session["history"].pop()
        session.modified = True
        return back_url
    # Should never happen but just in case
    else:
        return url_for("index.index_page")


def reset_history():
    session["history"] = [url_for("index.index_page")]


def clear_history():
    session["history"] = []
