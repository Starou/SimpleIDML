coverage-report-html: coverage
	@coverage html

coverage-report: coverage
	@coverage report -m

coverage: clean
	@coverage run --rcfile=coveragerc -a runtests.py

clean:
	@if [ -f .coverage ]; then rm .coverage; fi;
	@if [ -d htmlcov ]; then rm -rf htmlcov; fi;
