from server import config
import os

os.environ["TEST_SESSION"] = "true"

config.STATIC_ASSETS_MODE = "production"
config.STATIC_ASSETS_GZIP = "yes"
