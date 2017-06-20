
PYTHON_FILES := $(shell find yak_server -name '*.py')
PYTHON_FILES += $(shell find test -name '*.py')
PYTHON_FILES += setup.py

NOSE_OPTIONS = 

default: coverage lint

clean:
	find . -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .coverage htmlcov
	rm -rf docs/_build/*
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

docs: FORCE
	sphinx-build -b html docs/ docs/_build/

travis_test: FORCE
	nose2 $(NOSE_OPTIONS) -C --coverage yak_server/__init__.py test

test: FORCE
	nose2 $(NOSE_OPTIONS) test

unittest: FORCE
	nose2 $(NOSE_OPTIONS) test.unit

coverage: FORCE
	nose2 $(NOSE_OPTIONS) test.unit -C  --coverage yak_server/__init__.py --coverage-report html
	@sed -n 's/.*<span class="pc_cov">\(100%\)<\/span>.*/\nCoverage: \1\n/ p' htmlcov/index.html

pypytest: clean FORCE
	python setup.py bdist_wheel
	twine upload dist/* -r testpypi

lint: fix-whitespace
	@pylama --options=pylama_for_tests.ini test || true
	@pylama yak_server || true
	@pylama setup.py --ignore D100 || true

%.fixed_whitespace: %
	@if grep '^\s\+$$' --quiet $<; then sed -i 's/^\s\+$$//' $<; fi

fix-whitespace: $(addsuffix .fixed_whitespace, $(PYTHON_FILES))

venv:
	rm -rf venv
	virtualenv venv
	venv/bin/pip install nose2 cov-core pyusb
	@echo -e "\033[33mDon't forget to manually activate the virtual environment:\033[0m"
	@echo "source venv/bin/activate"

FORCE:
