# This file contains common administration commands. It is language-independent.

# Run this with 'make unittest' or 'make report="true" unittest'
unittest:
	if [ -z ${report} ]; then pytest unit_tests; else pytest --html=test-output/report.html --junitxml=test-output/unit-test-output.xml --cov-report=html:test-output/unit-test-cov-report unit_tests; fi

integrationtest:
	pytest --junitxml=test-output/integration-test-output.xml integration_tests

run:
	flask run --cert=/supporting-files/ssl.cert --key=/supporting-files/ssl.key

translations:
	pybabel extract -F babel.cfg -k _l -o messages.pot . && \
	pybabel update -i messages.pot -d server/translations -l cy

compile-translations:
	pybabel compile -d server/translations
