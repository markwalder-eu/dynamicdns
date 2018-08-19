
.DEFAULT_GOAL := coverage

################################################################################

install:
	pip install pipenv
	pipenv install
	pipenv install --dev
	npm install -g serverless
	npm install

test:
	pipenv run python -m unittest discover

coverage:
	pipenv run coverage run --source dynamicdns --branch --omit "*/__init__.py" -m unittest discover
	pipenv run coverage report

codecov: coverage
	pipenv run codecov -t $(CODECOV_TOKEN)

################################################################################

dev-release: VERSION=dev-$(shell git rev-parse --short HEAD)
dev-release: release

release: guard-VERSION
	git tag -a "$(VERSION)" -m "Release $(VERSION)"
	git push --tags
.PHONY: release

################################################################################

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

################################################################################
