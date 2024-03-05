import os
import redis
from landregistry.security_headers.header_defaults import DEFAULT_SCRIPT_HASHES


# RULES OF CONFIG:
# 1. No region specific code. Regions are defined by setting the OS environment variables appropriately to build up the
# desired behaviour.
# 2. No use of defaults when getting OS environment variables. They must all be set to the required values prior to the
# app starting.
# 3. This is the only file in the app where os.environ should be used.


# For logging
FLASK_LOG_LEVEL = os.environ["LOG_LEVEL"]

# For health route
COMMIT = os.environ["COMMIT"]

# This APP_NAME variable is to allow changing the app name when the app is running in a cluster. So that
# each app in the cluster will have a unique name.
APP_NAME = os.environ["APP_NAME"]

MAX_HEALTH_CASCADE = int(os.environ["MAX_HEALTH_CASCADE"])
# Following is an example of building the dependency structure used by the cascade route
# SELF can be used to demonstrate how it works (i.e. it will call it's own cascade
# route until MAX_HEALTH_CASCADE is hit)
# SELF = "http://localhost:8080"
# DEPENDENCIES = {"SELF": SELF}

DEFAULT_TIMEOUT = int(os.environ["DEFAULT_TIMEOUT"])

# Secret key for CSRF
SECRET_KEY = os.environ["SECRET_KEY"]

# Content security policy mode
# Can be either 'full' or 'report-only'
# 'full' will action the CSP and block violations
# 'report-only' will log but not block violations
# It is recommended to run in report-only mode for a while and monitor the logs
# to ensure that all violations are cleaned up to prevent your app from breaking
# when you switch it on fully
CONTENT_SECURITY_POLICY_MODE = os.environ["CONTENT_SECURITY_POLICY_MODE"]

# Static assets mode
# Can be either 'development' or 'production'
# 'development' will:
#   - Not gzip static assets
#   - Set far *past* expiry headers on static asset requests to prevent your browser from caching them
#   - Not add cachebusters to static asset query strings
# 'production' will:
#   - gzip static assets
#   - Set far *future* expiry headers on static asset requests to force browsers to cache for a long time
#   - Add cachebusters to static asset query strings to invalidate browsers' caches when necessary
STATIC_ASSETS_MODE = os.environ["STATIC_ASSETS_MODE"]
STATIC_ASSETS_GZIP = os.environ["STATIC_ASSETS_GZIP"]

# Put your full google analytics key in here, such as UA-126360441-1
# If you don't want google analytics, simply leave this line commented out and the config will default to False
# thereby disabling analytics entirely
# GOOGLE_ANALYTICS_KEY = os.environ['GOOGLE_ANALYTICS_KEY']

# Template switch
# Set this to either of the following values to switch between gov and hmlr templates
# hmlr
# govuk
BASE_TEMPLATE = os.environ["BASE_TEMPLATE"]

# Default to `httpOnly` session cookie served over HTTPS only.
# Adjust values in Dockerfile (and helm charts) if you require JS access to the session cookie.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"

# Google analytics
GOOGLE_ANALYTICS_KEY = os.environ.get("GOOGLE_ANALYTICS_KEY", False)

DEFAULT_TIMEOUT = int(os.environ['DEFAULT_TIMEOUT'])

# Search API URL
SEARCH_API_URL = os.environ['SEARCH_API_URL']
SEARCH_API_MAX_RESULTS = os.environ['SEARCH_API_MAX_RESULTS']

# Local Authority API URL
LOCAL_AUTHORITY_API_URL = os.environ['LOCAL_AUTHORITY_API_URL']

# Create cookies with secure flag
SESSION_COOKIE_SECURE = True

# Storage API
STORAGE_API_URL = os.environ['STORAGE_API_URL']
STORAGE_API_ROOT = os.environ['STORAGE_API_ROOT']

# Account API
ACCOUNT_API_URL = os.environ['ACCOUNT_API_URL']
ACCOUNT_API_ROOT = os.environ['ACCOUNT_API_ROOT']
NEW_USER_STATUS = os.environ['NEW_USER_STATUS']

# Audit API URL
AUDIT_API_URL = os.environ['AUDIT_API_URL']
AUDIT_API_ROOT = os.environ['AUDIT_API_ROOT']

# LLC1 API 'generate' endpoint
LLC1_API_URL = os.environ['LLC1_API_URL']

# Geoserver URL
GEOSERVER_URL = os.environ['GEOSERVER_URL']

# Flask-Session
PERMANENT_SESSION_LIFETIME = int(os.environ['PERMANENT_SESSION_LIFETIME'])
if os.environ.get("TEST_SESSION", "false") == "true":
    SESSION_TYPE = "filesystem"
else:
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(f"redis://{os.environ['SESSION_REDIS_HOST']}:{os.environ['SESSION_REDIS_PORT']}")
SESSION_USE_SIGNER = True

# Key for geoserver tokens
GEOSERVER_SECRET_KEY = os.environ['GEOSERVER_SECRET_KEY'].encode()

# Base layer API key and view name
MASTERMAP_API_KEY = os.environ['MASTERMAP_API_KEY']
MAP_BASE_LAYER_VIEW_NAME = os.environ['MAP_BASE_LAYER_VIEW_NAME']

WFS_SERVER_URL = os.environ['WFS_SERVER_URL']
WMTS_SERVER_URL = os.environ['WMTS_SERVER_URL']

# Search Local Land Charge API
SEARCH_LOCAL_LAND_CHARGE_API_URL = os.environ['SEARCH_LOCAL_LAND_CHARGE_API_URL']

# Search fee in pence
SEARCH_FEE_IN_PENCE = os.environ['SEARCH_FEE_IN_PENCE']

# OS Terms and Conditions Link (displayed on copyright message on map pages)
OS_TERMS_CONDITIONS_LINK = os.environ['OS_TERMS_CONDITIONS_LINK']

# This APP_NAME variable is to allow changing the app name when the app is running in a cluster. So that
# each app in the cluster will have a unique name.
APP_NAME = os.environ['APP_NAME']

# SECRET_KEY used for CSRF protection
SECRET_KEY = os.environ['SECRET_KEY']

# GOV_PAY_URL
GOV_PAY_URL = os.environ['GOV_PAY_URL']

# GOV_PAY_API_KEY
GOV_PAY_API_KEY = os.environ['GOV_PAY_API_KEY']
OPENRESTY_URL = os.environ['OPENRESTY_URL']

# Feedback
FEEDBACK_URL = os.environ['FEEDBACK_URL']

# Charges per page
CHARGES_PER_PAGE = os.environ['CHARGES_PER_PAGE']

# 'Contact Us' URL
CONTACT_US_URL = os.environ['CONTACT_US_URL']
CONTACT_US_WELSH_URL = os.environ['CONTACT_US_WELSH_URL']

# Report API
REPORT_API_BASE_URL = os.environ['REPORT_API_BASE_URL']

# PDF generation polling (seconds)
PDF_GENERATION_POLL = int(os.environ['PDF_GENERATION_POLL'])

# Authentication API
AUTHENTICATION_URL = os.environ['AUTHENTICATION_URL']

# Accessibility statement dates
ACCESSIBILITY_STATEMENT_PUBLISH = os.environ['ACCESSIBILITY_STATEMENT_PUBLISH']
ACCESSIBILITY_STATEMENT_UPDATE = os.environ['ACCESSIBILITY_STATEMENT_UPDATE']

MAINTAIN_API_URL = os.environ['MAINTAIN_API_URL']

INSPIRE_API_ROOT = os.environ['INSPIRE_API_ROOT']

HOME_PAGE_CY_URL = os.environ['HOME_PAGE_CY_URL']
HOME_PAGE_EN_URL = os.environ['HOME_PAGE_EN_URL']

# Default page size for pagination
DEFAULT_PAGE_SIZE = int(os.environ['DEFAULT_PAGE_SIZE'])

RELEASE_NOTICES_URL = os.environ['RELEASE_NOTICES_URL']

# MAX_HEALTH_CASCADE used for cascading health checks
MAX_HEALTH_CASCADE = os.environ['MAX_HEALTH_CASCADE']
DEPENDENCIES = {"Search API": os.environ['SEARCH_API_ROOT'],
                "LLC1 API": os.environ['LLC1_API_ROOT'],
                "Audit API": os.environ['AUDIT_API_ROOT'],
                "Account API": os.environ['ACCOUNT_API_ROOT'],
                "Storage API": os.environ['STORAGE_API_ROOT'],
                "Search Local Land Charge API": os.environ['SEARCH_LOCAL_LAND_CHARGE_API_URL'],
                "Report API": os.environ['REPORT_API_BASE_URL'],
                "Authentication API": os.environ['AUTHENTICATION_URL'],
                "Inspire API": os.environ['INSPIRE_API_ROOT']}

# Security header things
SECURITY_CSP_SCRIPT_HASHES = f"{DEFAULT_SCRIPT_HASHES} 'sha256-cl2QRSoYUeszO98VLlxSOD9YleEFNbw4vz9QAaZFrT0='"
