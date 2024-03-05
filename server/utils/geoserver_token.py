from cryptography.fernet import Fernet
from server import config
from flask import session


def geoserver_token():
    f = Fernet(config.GEOSERVER_SECRET_KEY)
    token = f.encrypt(session.sid.encode())
    return token.decode()
