# Set the base image to the s2i image
FROM docker-registry/stp/stp-s2i-python-extended:3.9

# Switch from s2i's non-root user back to root for the following commmands
USER root

# Create a user that matches dev-env runner's host user
# This will ensure generated files like .pyc have the right permissions if running on a Linux host
ARG OUTSIDE_UID
ARG OUTSIDE_GID
RUN groupadd --force --gid $OUTSIDE_GID containergroup && \
 useradd --uid $OUTSIDE_UID --gid $OUTSIDE_GID containeruser

ENV PYTHONPATH /src

# Install node modules
# These are installed outside of the mounted volume and nodejs is instructed to look for them by setting NODE_PATH / PATH
# This is to avoid the fact that the volume will wipe out anything that gets added when the container is being built
ENV NODE_PATH='/supporting-files/node_modules' \
  PATH="/supporting-files/node_modules/.bin:${PATH}" \
  NODE_ENV='production' \
  NPM_CONFIG_PRODUCTION='false'
ADD .npmrc /supporting-files/
ADD package*.json /supporting-files/
RUN cd /supporting-files \
  && npm install --loglevel=error \
  && chown -R containeruser: /supporting-files

# Get the python environment ready.
ADD requirements_test.txt requirements_test.txt
ADD requirements.txt requirements.txt
RUN pip3 install -q -r requirements.txt && \
  pip3 install -q -r requirements_test.txt

# Any unique environment variables your config.py needs should be added as ENV entries here
# These env vars will need defining in any deployed environment
# These values are not the same as our production environment
ENV APP_MODULE='server.main:app' \
  BASE_TEMPLATE='govuk' \
  CONTENT_SECURITY_POLICY_MODE='full' \
  DEFAULT_TIMEOUT='30' \
  FLASK_APP=server.main \
  FLASK_DEBUG=1 \
  LOG_LEVEL=DEBUG \
  STATIC_ASSETS_MODE='development' \
  STATIC_ASSETS_GZIP='no' \
  AUDIT_API_URL="http://audit-stub-api:8080/v1" \
  AUDIT_API_ROOT="http://audit-stub-api:8080" \
  ACCOUNT_API_URL="http://dev-search-account-api:8080/v1.0" \
  ACCOUNT_API_ROOT="http://dev-search-account-api:8080" \
  NEW_USER_STATUS="Active" \
  SEARCH_API_URL="http://dev-search-service-search-api:8080/v2.0" \
  SEARCH_API_ROOT="http://dev-search-service-search-api:8080" \
  OPENRESTY_URL="https://localhost:8081" \
  STORAGE_API_URL="http://storage-api:8080/v1.0/storage" \
  STORAGE_API_ROOT="http://storage-api:8080" \
  LLC1_API_URL="http://llc1-document-api:8080/v1.0" \
  LLC1_API_ROOT="http://llc1-document-api:8080" \
  WFS_SERVER_URL="https://wfs.viaeuropa.uk.com" \
  GOV_PAY_URL="https://publicapi.payments.service.gov.uk/v1/payments" \
  WMTS_SERVER_URL="https://tile.viaeuropa.uk.com" \
  GEOSERVER_URL="https://localhost:8081" \
  SEARCH_LOCAL_LAND_CHARGE_API_URL="http://search-local-land-charge-api:8080" \
  SEARCH_FEE_IN_PENCE=1500 \
  OS_TERMS_CONDITIONS_LINK="https://www.ordnancesurvey.co.uk/business-government/licensing-agreements/terms-hmlr-scotland" \
  MASTERMAP_API_KEY="dummy-mastermap-api-key" \
  MAP_BASE_LAYER_VIEW_NAME="map-base-layer-view-name" \
  SECRET_KEY=dummy-secret-key \
  GOV_PAY_API_KEY=dummy-gov-pay-api-key \
  MAX_HEALTH_CASCADE=6 \
  DEFAULT_PAGE_SIZE=10 \
  FEEDBACK_URL="https://forms.office.com/Pages/ResponsePage.aspx?id=qAljI0soV06ns_x2dzb2ndpkPp2GFRdNvViFXghN4kNUMzc5N1FEWDI5QVgyNlBNVkpGMUw2Rk1TQyQlQCN0PWcu" \
  LOCAL_AUTHORITY_API_URL=http://local-authority-api:8080 \
  SEARCH_API_MAX_RESULTS=200 \
  CONTACT_US_URL="https://customerhelp.landregistry.gov.uk/local-land-charges" \
  CONTACT_US_WELSH_URL="https://customerhelp.landregistry.gov.uk/local-land-charges-cy" \
  REPORT_API_BASE_URL="http://report-api:8080" \
  AUTHENTICATION_URL="http://dev-search-authentication-api:8080" \
  ACCESSIBILITY_STATEMENT_PUBLISH="07/12/2022" \
  ACCESSIBILITY_STATEMENT_UPDATE="07/12/2022" \
  PDF_GENERATION_POLL=5 \
  CHARGES_PER_PAGE=25 \
  MAINTAIN_API_URL="http://maintain-api:8080/v1.0/maintain" \
  INSPIRE_API_ROOT="http://inspire-api:8080" \
  PERMANENT_SESSION_LIFETIME=5700 \
  SESSION_REDIS_HOST="redis" \
  SESSION_REDIS_PORT="6379" \
  GEOSERVER_SECRET_KEY="dummy-geoserver-secret-key" \
  HOME_PAGE_CY_URL="/dummy-welsh" \
  HOME_PAGE_EN_URL="/dummy-english" \
  RELEASE_NOTICES_URL="TEST" \
  GOOGLE_ANALYTICS_KEY="dummy-google-analytics-key"

# THESE env vars are just for local running, so they're apart from the rest for clarity
ENV APP_NAME=search-local-land-charge-ui \
  GUNICORN_ARGS='--reload' \
  PYTHONPATH=/src \
  WEB_CONCURRENCY='2'

# If you are building a govuk service - switch BASE_TEMPLATE above to be 'govuk'

# Set the user back to a non-root user like the s2i run script expects
# When creating files inside the docker container, this will also prevent the files being owned
# by the root user, which would cause issues if running on a Linux host machine
USER containeruser

CMD ["./run.sh"]
