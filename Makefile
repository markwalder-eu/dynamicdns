
msg=@printf "\n\033[0;01m>>> %s\033[0m\n" $1

################################################################################

.DEFAULT_GOAL := dev-release

install:
	$(call msg,"Install required software")
	pip install pipenv
	pipenv install
	pipenv install --dev
	npm install -g serverless
	npm install

test:
	$(call msg,"Run Unit Tests")
	pipenv run python -m unittest discover

coverage:
	$(call msg,"Run Codecoverage")
	pipenv run coverage run --source dynamicdns --branch --omit "*/__init__.py" -m unittest discover
	pipenv run coverage report

codecov: coverage
	$(call msg,"Upload codecoverage results to codecov.io")
	pipenv run codecov -t $(CODECOV_TOKEN)

################################################################################

dev-release: VERSION=dev-$(shell git rev-parse --short HEAD)
dev-release: release

release: guard-VERSION
	$(call msg,"Make release $(VERSION)")
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
