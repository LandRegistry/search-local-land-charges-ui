import json
import base64


def check_valid_base64_json_cookie(cookie_base64):
    try:
        cookie_json = json.loads(base64.b64decode(cookie_base64))
        return True, cookie_json
    except Exception:
        return False, {}


def encode_base64_json_cookie(cookie_json):
    return base64.b64encode(json.dumps(cookie_json).encode())
