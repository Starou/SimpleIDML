coveralls:
	@coverage run --rcfile=coveragerc runtests.py
	@coveralls -y coveralls.yaml -d .coverage

coverage-report: coverage
	@coverage report -m

coverage:
	@coverage run --rcfile=coveragerc runtests.py
