
.DEFAULT_GOAL := coverage

UNAME := $(shell uname)

ifeq ($(UNAME), Linux)
OS = linux
else
OS = windows
endif

################################################################################

install:
	pip install pipenv
	pipenv install
	pipenv install --dev
	npm install -g serverless
	npm install
.PHONY: install

test:
	pipenv run python -m unittest discover
.PHONY: test

coverage:
	pipenv run coverage run --source dynamicdns --branch --omit "*/__init__.py" -m unittest discover
	pipenv run coverage report
.PHONY: coverage

codecov: coverage
	pipenv run codecov -t $(CODECOV_TOKEN)
.PHONY: codecov

################################################################################
# Client Ops

dev-release: VERSION = $(shell git describe)
dev-release: release

release: $(OS)-guard-VERSION
	@echo $(VERSION)
	#git tag -a "$(VERSION)" -m "Release $(VERSION)"
	#git push --tags
.PHONY: release

client-config: config/client.config.template
	@echo $@

################################################################################
# Server Ops

deploy: version config/serverless-$(STAGE).config.yml $(OS)-guard-STAGE
	@serverless deploy --stage=$(STAGE)
	@serverless create_domain --stage=$(STAGE)

version:
	@echo no = \"$(shell git describe)\" > dynamicdns/version.py

config/serverless-$(STAGE).config.yml: $(OS)-guard-STAGE $(OS)-guard-API_DOMAIN_NAME $(OS)-guard-S3_REGION $(OS)-guard-S3_BUCKET $(OS)-guard-S3_KEY $(OS)-guard-API_DOMAIN_CERTIFICATE_NAME
	@echo apiDomainName: $(API_DOMAIN_NAME)> $@
	@echo s3Region: $(S3_REGION)>> $@
	@echo s3Bucket: $(S3_BUCKET)>> $@
	@echo s3Key: $(S3_KEY)>> $@
	@echo apiDomainCertificateName: \'$(API_DOMAIN_CERTIFICATE_NAME)\'>> $@

clean: $(OS)-guard-STAGE
	@rm -rf config/serverless-$(STAGE).config.yml

################################################################################

linux-guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

windows-guard-%:
	@ if "$(${*})" == "" ( \
		echo Environment variable $* not set & \
		exit 1 \
	) 
	
################################################################################
