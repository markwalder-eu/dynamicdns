
.DEFAULT_GOAL := coverage

UNAME := $(shell uname)

SHELL := /bin/bash 

################################################################################
# Development Targets

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
# Release Targets

dev-release: VERSION = dev-$(shell date +%Y%m%d-%H%M%S)
dev-release: release

release: guard-VERSION
	git tag -a "$(VERSION)" -m "Release $(VERSION)"
	git push --tags
.PHONY: release

################################################################################
# Configuration Targets

clean-config: guard-STAGE
	@rm -rf config/client-$(STAGE).config
	@rm -rf config/server-$(STAGE).config
	@rm -rf config/serverless-$(STAGE).config.yml
.PHONY: clean-config

create-config: config \
	guard-STAGE \
	guard-URL \
	guard-DNS_HOSTNAME \
	guard-SHARED_SECRET \

	S3_REGION
	ROUTE53_ZONE_ID
	@test -n "$(ROUTE53_RECORD_TTL)" # $$ROUTE53_RECORD_TTL
	@test -n "$(ROUTE53_RECORD_TYPE)" # $$ROUTE53_RECORD_TYPE
	@test -n "$(SHARED_SECRET)

	config/client-$(STAGE).config \
	config/server-$(STAGE).config \
	config/serverless-$(STAGE).config.yml
.PHONY: create-config

config/client-$(STAGE).config: guard-STAGE
	@test -n "$(URL)" # $$URL
	@test -n "$(DNS_HOSTNAME)" # $$DNS_HOSTNAME
	@test -n "$(SHARED_SECRET)" # $$SHARED_SECRET

	@echo \# Base URL of API Dynamic DNS server> $@
	@echo \# e.g. url=https://api.domain.com>> $@
	@echo url=$(URL)>> $@
	@echo >> $@
	@echo \# Hostname of DNS and config entry>> $@
	@echo \# e.g. hostname=home.domain.com>> $@
	@echo hostname=$(DNS_HOSTNAME)>> $@
	@echo >> $@
	@echo \# Shared secret to use for communication>> $@
	@echo \# e.g. sharedsecret=ZDhszNKMbmuFYBhZgAuzoQFbmcqM6CYb>> $@
	@echo sharedsecret=$(SHARED_SECRET)>> $@

config/server-$(STAGE).config: guard-STAGE
	@test -n "$(DNS_HOSTNAME)" # $$DNS_HOSTNAME
	@test -n "$(ROUTE53_REGION)" # $$ROUTE53_REGION
	@test -n "$(ROUTE53_ZONE_ID)" # $$ROUTE53_ZONE_ID
	@test -n "$(ROUTE53_RECORD_TTL)" # $$ROUTE53_RECORD_TTL
	@test -n "$(ROUTE53_RECORD_TYPE)" # $$ROUTE53_RECORD_TYPE
	@test -n "$(SHARED_SECRET)" # $$SHARED_SECRET

	@echo "{"> $@
	@echo "	\"$(DNS_HOSTNAME)\": {">> $@
	@echo "		\"route_53_region\": \"$(ROUTE53_REGION)\",">> $@
	@echo "		\"route_53_zone_id\": \"$(ROUTE53_ZONE_ID)\",">> $@
	@echo "		\"route_53_record_ttl\": $(ROUTE53_RECORD_TTL),">> $@
	@echo "		\"route_53_record_type\": \"$(ROUTE53_RECORD_TYPE)\",">> $@
	@echo "		\"shared_secret\": \"$(SHARED_SECRET)\"">> $@
	@echo "	}">> $@
	@echo "}">> $@

config/serverless-$(STAGE).config.yml: guard-STAGE
	@test -n "$(API_DOMAIN_NAME)" # $$API_DOMAIN_NAME
	@test -n "$(S3_REGION)" # $$S3_REGION
	@test -n "$(S3_BUCKET)" # $$S3_BUCKET
	@test -n "$(S3_KEY)" # $$S3_KEY
	@test -n "$(API_DOMAIN_CERTIFICATE_NAME)" # $$API_DOMAIN_CERTIFICATE_NAME

	@echo apiDomainName: $(API_DOMAIN_NAME)> $@
	@echo s3Region: $(S3_REGION)>> $@
	@echo s3Bucket: $(S3_BUCKET)>> $@
	@echo s3Key: $(S3_KEY)>> $@
	@echo apiDomainCertificateName: \'$(API_DOMAIN_CERTIFICATE_NAME)\'>> $@

################################################################################
# Client Targets

run: config/client-$(STAGE).config guard-STAGE guard-URL
	@bash <(curl -sSL https://$(URL)/dynamicdns-v1/script) -c config/client-$(STAGE).config

################################################################################
# Deployment Targets

version:
	@echo -n $(shell git describe) > dynamicdns/version

config:
	mkdir -p config

deploy: guard-STAGE version config config/serverless-$(STAGE).config.yml
	@serverless deploy --stage=$(STAGE)
	@serverless create_domain --stage=$(STAGE)

deploy-dev:
	$(eval export STAGE=dev)
	$(eval export DNS_HOSTNAME=$(DEV_DNS_HOSTNAME))
	$(eval export SHARED_SECRET=$(DEV_SHARED_SECRET))
	$(eval export API_DOMAIN_NAME=$(DEV_API_DOMAIN_NAME))
	$(eval export API_DOMAIN_CERTIFICATE_NAME=$(DEV_API_DOMAIN_CERTIFICATE_NAME))
	$(eval export ROUTE53_REGION=$(DEV_ROUTE53_REGION))
	$(eval export ROUTE53_ZONE_ID=$(DEV_ROUTE53_ZONE_ID))
	$(eval export ROUTE53_RECORD_TTL=$(DEV_ROUTE53_RECORD_TTL))
	$(eval export ROUTE53_RECORD_TYPE=$(DEV_ROUTE53_RECORD_TYPE))
	$(eval export S3_REGION=$(DEV_S3_REGION))
	$(eval export S3_BUCKET=$(DEV_S3_BUCKET))
	$(eval export S3_KEY=$(DEV_S3_KEY))
	$(MAKE) deploy
.PHONY: deploy-dev

deploy-prd:
	$(eval export STAGE=prd)
	$(eval export DNS_HOSTNAME=$(PRD_DNS_HOSTNAME))
	$(eval export SHARED_SECRET=$(PRD_SHARED_SECRET))
	$(eval export API_DOMAIN_NAME=$(PRD_API_DOMAIN_NAME))
	$(eval export API_DOMAIN_CERTIFICATE_NAME=$(PRD_API_DOMAIN_CERTIFICATE_NAME))
	$(eval export ROUTE53_REGION=$(PRD_ROUTE53_REGION))
	$(eval export ROUTE53_ZONE_ID=$(PRD_ROUTE53_ZONE_ID))
	$(eval export ROUTE53_RECORD_TTL=$(PRD_ROUTE53_RECORD_TTL))
	$(eval export ROUTE53_RECORD_TYPE=$(PRD_ROUTE53_RECORD_TYPE))
	$(eval export S3_REGION=$(PRD_S3_REGION))
	$(eval export S3_BUCKET=$(PRD_S3_BUCKET))
	$(eval export S3_KEY=$(PRD_S3_KEY))
	$(MAKE) deploy
.PHONY: deploy-prd

################################################################################

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

################################################################################
