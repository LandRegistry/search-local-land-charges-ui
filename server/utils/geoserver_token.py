from cryptography.fernet import Fernet
from flask import session

from server import config


def geoserver_token(url=None):
    f = Fernet(config.GEOSERVER_SECRET_KEY)
    if url:
        token = f.encrypt(url.encode())
    else:
        token = f.encrypt(session.sid.encode())
    return token.decode()
