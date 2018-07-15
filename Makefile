
msg=@printf "\n\033[0;01m>>> %s\033[0m\n" $1

################################################################################

.DEFAULT_GOAL := dev-release

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
