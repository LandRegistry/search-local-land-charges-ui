# search-local-land-charge-ui

This repository contains a flask application structured in the way that all Land Registry flask user interfaces should be structured going forwards.

## Quick start

### Docker

This app supports the [common-dev-env](https://github.com/LandRegistry/common-dev-env) so adding the following to your dev-env config file is enough:

```YAML
  search-local-land-charge-ui:
    repo: git@repository-host:local_land_charges/search-local-land-charge-ui.git
    branch: master
```

The Docker image it creates (and runs) will install all necessary requirements and set all environment variables for you.

### Standalone

#### Environment variables to set

* PYTHONUNBUFFERED *(suggested value: yes)*
* PORT
* LOG_LEVEL
* COMMIT
* APP_NAME
* MAX_HEALTH_CASCADE *(suggested value: 6)*
* DEFAULT_TIMEOUT *(suggested value: 30)*
* SECRET_KEY
* CONTENT_SECURITY_POLICY_MODE *(suggested value: full)*
* STATIC_ASSETS_MODE
* BASE_TEMPLATE *(suggested value: hmlr)*
* SESSION_COOKIE_HTTPONLY *(suggested value: True)*
* SESSION_COOKIE_SECURE *(suggested value: True)*
* SPRINGBOOT_MVC_SKELETONXL_API

##### When not using gunicorn

* FLASK_APP *(suggested value: server/main.py)*
* FLASK_DEBUG *(suggested value: 1)*

#### Running (when not using gunicorn)

(The third party libraries are defined in requirements.txt and can be installed using pip)

```shell
python3 -m flask run
or
flask run
or
make run
```

## Code

### Formatting

This application uses [Black](https://github.com/psf/black) to format its Python code in a consistent and predictable way. Please ensure you run `black . --line-length 119` to format your code prior to raising a merge request.

### Linting

This application uses [Flake8](https://gitlab.com/pycqa/flake8) to lint its Python code to check for errors and conformity with the PEP8 standards. After formatting, please ensure you run `flake8 .` to lint your code prior to raising a merge request.

### JavaScript formatting and linting

For the JavaScript side, this application uses a combination of the [HMLR ESLint config](https://github.com/LandRegistry/eslint-config) and [Prettier](https://prettier.io/) to check for errors and apply consistent formatting. Please remember to run `npm run lint:fix` prior to raising a merge request which will raise any errors and if there are none, prettify the code.

## Testing

### Unit tests

The unit tests are contained in the unit_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for unit testing. To run the tests use the following command:

```bash
make unittest
(or just py.test)
```

To run them and output a coverage report and a junit xml file run:

```bash
make report="true" unittest
```

These files get added to a test-output folder. The test-output folder is created if doesn't exist.

You can run these commands in the app's running container via `docker-compose exec search-local-land-charge-ui <command>` or `exec search-local-land-charge-ui <command>`. There is also an alias: `unit-test search-local-land-charge-ui` and `unit-test search-local-land-charge-ui -r` will run tests and generate reports respectively.

### Integration tests

The integration tests are contained in the integration_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for integration testing. To run the tests and output a junit xml use the following command:

```shell
make integrationtest
(or py.test integration_tests)
```

This file gets added to the test-output folder. The test-output folder is created if doesn't exist.

To run the integration tests if you are using the common dev-env you can run `docker-compose exec search-local-land-charge-ui make integrationtest` or, using the alias, `integration-test search-local-land-charge-ui`.

### Universal Development Environment support

Provided via `configuration.yml`, `Dockerfile` and `fragments/docker-compose-fragment.yml`.

`configuration.yml` lists the commodities the dev env needs to spin up e.g. postgres. The ELK stack is spun up when "logging" is present.

The `docker-compose-fragment.yml` contains the service definiton, including the external port to map to, sharing the app source folder so the files don't need to be baked into the image, and redirection of the stdout logs to logstash via syslog.

The `Dockerfile` simply sets the APP_NAME environment variable and installs the third party library requirements. Any further app-specific variables or commands can be added here.

