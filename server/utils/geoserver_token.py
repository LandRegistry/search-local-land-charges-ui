from cryptography.fernet import Fernet
from flask import session

from server import config


def geoserver_token():
    f = Fernet(config.GEOSERVER_SECRET_KEY)
    token = f.encrypt(session.sid.encode())
    return token.decode()
