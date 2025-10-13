TEMPDIR_INFOSECTOOLS = /tmp/infosec-dev-tools
VENV = .venv
COVERAGE_REPORT_FORMAT = 'html'
DOCKERFILE ?= Dockerfile
CONTAINER_WEBPORT ?= 8000
HOST_WEBPORT=$(CONTAINER_WEBPORT)
CONTEXT = .
CONTAINER_ENGINE = podman
APP_NAME ?= distributors
PYTHON_CMD = uv run
QUAY_ORG ?= redhat-services-prod
QUAY_REPOSITORY ?= distributors-tenant/$(APP_NAME)-backend
IMAGE = quay.io/$(QUAY_ORG)/$(QUAY_REPOSITORY)

# Determine the container engine
ifneq ($(shell command -v "podman"),)
	CONTAINER_ENGINE = podman
else ifneq ($(shell command -v "docker"),)
	CONTAINER_ENGINE = docker
else
	$(error "No container engine found. Install either podman or docker.")
endif

# Determine IMAGE_TAG and LABEL
BASE_IMAGE_TAG=$(shell git rev-parse --short=7 HEAD)
ifdef ghprbPullId
	IMAGE_TAG=pr-$(ghprbPullId)-$(BASE_IMAGE_TAG)
	LABEL=$(shell echo "--label quay.expires-after=1h")
else ifdef gitlabMergeRequestId
	IMAGE_TAG=mr-$(gitlabMergeRequestId)-$(BASE_IMAGE_TAG)
	LABEL=$(shell echo "--label quay.expires-after=1h")
else
	IMAGE_TAG=$(BASE_IMAGE_TAG)
endif

run: venv_check install
	uv run fastapi dev src/main.py

install_pre_commit: venv_check
	# Remove any outdated tools
	rm -rf $(TEMPDIR_INFOSECTOOLS)
	# Clone up-to-date tools
	git clone https://gitlab.corp.redhat.com/infosec-public/developer-workbench/tools.git $(TEMPDIR_INFOSECTOOLS)

	# Cleanup installed old tools
	$(TEMPDIR_INFOSECTOOLS)/scripts/uninstall-legacy-tools

	# install pre-commit and configure it on our repo
	$(TEMPDIR_INFOSECTOOLS)/rh-pre-commit/quickstart.sh -r .

	rm -rf $(TEMPDIR_INFOSECTOOLS)

venv_check:
	@uv venv --help > /dev/null 2>&1 || (echo "uv not installed" && exit 1)
	@test -d .venv || (echo "No uv virtual environment found. Run 'uv venv' to create one." && exit 1)

venv_create:
	@test -d .venv && echo "Virtual environment already exists" || uv venv $(VENV)

quay_login:
	$(CONTAINER_ENGINE) login quay.io

lint: install_dev
	uv run pre-commit run --all

install: venv_check
	uv sync

install_dev: venv_check
	uv sync --dev

clean:
	rm -rf __pycache__
	find . -name "*.pyc" -exec rm -f {} \;

test: venv_check install_dev
	${PYTHON_CMD} pytest test/

coverage: venv_check install_dev
	${PYTHON_CMD} pytest test/ --cov=src --cov-report=term --cov-report=html

coverage-ci: venv_check install_dev
	${PYTHON_CMD} pytest test/ --cov=src --cov-report=term --cov-report=xml

build-image:
	$(CONTAINER_ENGINE) buildx build --platform linux/amd64 -t $(IMAGE):$(IMAGE_TAG) -f $(DOCKERFILE) $(LABEL) $(CONTEXT)

run-container:
	$(CONTAINER_ENGINE) run -it --rm -p $(HOST_WEBPORT):$(CONTAINER_WEBPORT) $(IMAGE):$(IMAGE_TAG) runserver 0.0.0.0:8000

namespace_check:
ifndef NAMESPACE
	$(error NAMESPACE not defined, please specify a NAMESPACE environment varible)
endif

bonfire_process:
	bonfire process $(APP_NAME) \
		-p $(APP_NAME)-backend/IMAGE=$(IMAGE) -p $(APP_NAME)-backend/IMAGE_TAG=$(IMAGE_TAG) \
		-p $(APP_NAME)-backend/SALESFORCE_DOMAIN="$(SALESFORCE_DOMAIN)" \
		-p $(APP_NAME)-backend/SALESFORCE_USERNAME="$(SALESFORCE_USERNAME)" \
		-p $(APP_NAME)-backend/SALESFORCE_CONSUMER_KEY="$(SALESFORCE_CONSUMER_KEY)" \
		-p $(APP_NAME)-backend/SALESFORCE_KEYSTORE_DATA="$(SALESFORCE_KEYSTORE_DATA)" \
		-p $(APP_NAME)-backend/SALESFORCE_KEYSTORE_PASSWORD="$(SALESFORCE_KEYSTORE_PASSWORD)" \
		-p $(APP_NAME)-backend/SALESFORCE_CERT_ALIAS="$(SALESFORCE_CERT_ALIAS)" \
		-p $(APP_NAME)-backend/SALESFORCE_CERT_PASSWORD="$(SALESFORCE_CERT_PASSWORD)" \
		-n default

bonfire_reserve_namespace:
	@bonfire namespace reserve -f --duration 24h

bonfire_release_namespace: namespace_check
	bonfire namespace release $(NAMESPACE) -f

bonfire_user_namespaces:
	bonfire namespace list --mine

bonfire_deploy: namespace_check
	bonfire deploy $(APP_NAME) \
		-p $(APP_NAME)-backend/IMAGE=$(IMAGE) -p $(APP_NAME)-backend/IMAGE_TAG=$(IMAGE_TAG) \
		-p $(APP_NAME)-backend/SALESFORCE_DOMAIN="$(SALESFORCE_DOMAIN)" \
		-p $(APP_NAME)-backend/SALESFORCE_USERNAME="$(SALESFORCE_USERNAME)" \
		-p $(APP_NAME)-backend/SALESFORCE_CONSUMER_KEY="$(SALESFORCE_CONSUMER_KEY)" \
		-p $(APP_NAME)-backend/SALESFORCE_KEYSTORE_DATA="$(SALESFORCE_KEYSTORE_DATA)" \
		-p $(APP_NAME)-backend/SALESFORCE_KEYSTORE_PASSWORD="$(SALESFORCE_KEYSTORE_PASSWORD)" \
		-p $(APP_NAME)-backend/SALESFORCE_CERT_ALIAS="$(SALESFORCE_CERT_ALIAS)" \
		-p $(APP_NAME)-backend/SALESFORCE_CERT_PASSWORD="$(SALESFORCE_CERT_PASSWORD)" \
		-n $(NAMESPACE)
