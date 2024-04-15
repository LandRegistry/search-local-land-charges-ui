import os

from server import config

os.environ["TEST_SESSION"] = "true"

config.STATIC_ASSETS_MODE = "production"
config.STATIC_ASSETS_GZIP = "yes"
