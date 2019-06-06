# bulby house style
.PHONY: test
test:
	which -s pytest || echo "pip3 install --user pytest"
	which -s pytest-cov || echo "pip3 install --user pytest-cov"
	python3 -m pytest --cov=workflow --cov-fail-under 75 tests

.PHONY: checks
checks:
	which -s flake8 || echo "pip3 install --user flake8"
	which -s isort || echo "pip3 install --user isort"
	which -s mypy || echo "pip3 install --user mypy"
	which -s bandit || echo "pip3 install --user bandit"
	
	flake8 --exclude=.env,venv --show-source --statistics --count --max-complexity=5

	mypy -p workflow \
    --ignore-missing-imports \
    --disallow-untyped-calls \
    --disallow-untyped-decorators \
    --check-untyped-defs \
    --disallow-incomplete-defs

	isort --recursive --check-only ./workflow

	bandit -r workflow --exclude=.env,venv -lll -iii