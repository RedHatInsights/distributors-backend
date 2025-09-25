TEMPDIR_INFOSECTOOLS = /tmp/infosec-dev-tools
VENV = .venv
COVERAGE_REPORT_FORMAT = 'html'
DOCKERFILE ?= Dockerfile
CONTAINER_WEBPORT ?= 8000
HOST_WEBPORT=$(CONTAINER_WEBPORT)
CONTEXT = .
CONTAINER_ENGINE = podman
BONFIRE_CONFIG = .bonfirecfg.yaml
CLOWDAPP_TEMPLATE ?= clowdapp.yaml
APP_NAME ?= distributors-backend
PYTHON_CMD = uv run
QUAY_ORG ?= cloudservices
QUAY_REPOSITORY ?= $(APP_NAME)
IMAGE = quay.io/$(QUAY_ORG)/$(QUAY_REPOSITORY)
export ACG_CONFIG = cdappconfig.json

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
	${PYTHON_CMD} manage.py runserver

migrate: venv_check
	${PYTHON_CMD} manage.py migrate

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
	echo -n "$(QUAY_TOKEN)" | $(CONTAINER_ENGINE) login quay.io --username $(QUAY_USER) --password-stdin

lint: install_dev
	uv run pre-commit run --all

install: venv_check
	uv sync

install_dev: venv_check
	uv sync --dev

run_dev: venv_check
	uv run fastapi dev src/main.py

clean:
	rm -rf __pycache__
	find . -name "*.pyc" -exec rm -f {} \;

test: venv_check install_dev
	${PYTHON_CMD} manage.py test

smoke-test: venv_check install_dev
	@echo "Running smoke tests"

coverage: venv_check install_dev
	coverage run --source="." manage.py test
	coverage $(COVERAGE_REPORT_FORMAT)

coverage-ci: COVERAGE_REPORT_FORMAT=xml
coverage-ci: coverage

build-image:
	$(CONTAINER_ENGINE) buildx build --platform linux/amd64 -t $(IMAGE):$(IMAGE_TAG) -f $(DOCKERFILE) $(LABEL) $(CONTEXT)

run-container:
	$(CONTAINER_ENGINE) run -it --rm -p $(HOST_WEBPORT):$(CONTAINER_WEBPORT) $(IMAGE):$(IMAGE_TAG) runserver 0.0.0.0:8000

push-image:
	$(CONTAINER_ENGINE) push $(IMAGE):$(IMAGE_TAG)

namespace_check:
ifndef NAMESPACE
	$(error NAMESPACE not defined, please specify a NAMESPACE environment varible)
endif

bonfire_process:
	bonfire process -c $(BONFIRE_CONFIG) $(APP_NAME) \
		-p service/IMAGE=$(IMAGE) -p service/IMAGE_TAG=$(IMAGE_TAG) \
		-p service/SALESFORCE_DOMAIN="$(SALESFORCE_DOMAIN)" \
		-p service/SALESFORCE_USERNAME="$(SALESFORCE_USERNAME)" \
		-p service/SALESFORCE_CONSUMER_KEY="$(SALESFORCE_CONSUMER_KEY)" \
		-p service/SALESFORCE_KEYSTORE_DATA="$(SALESFORCE_KEYSTORE_DATA)" \
		-p service/SALESFORCE_KEYSTORE_PASSWORD="$(SALESFORCE_KEYSTORE_PASSWORD)" \
		-p service/SALESFORCE_CERT_ALIAS="$(SALESFORCE_CERT_ALIAS)" \
		-p service/SALESFORCE_CERT_PASSWORD="$(SALESFORCE_CERT_PASSWORD)" \
		-n default

bonfire_reserve_namespace:
	@bonfire namespace reserve -f --duration 24h

bonfire_release_namespace: namespace_check
	bonfire namespace release $(NAMESPACE) -f

bonfire_user_namespaces:
	bonfire namespace list --mine

bonfire_deploy: namespace_check
	bonfire deploy -c $(BONFIRE_CONFIG) $(APP_NAME) \
		-p service/IMAGE=$(IMAGE) -p service/IMAGE_TAG=$(IMAGE_TAG) \
		-p service/SALESFORCE_DOMAIN="$(SALESFORCE_DOMAIN)" \
		-p service/SALESFORCE_USERNAME="$(SALESFORCE_USERNAME)" \
		-p service/SALESFORCE_CONSUMER_KEY="$(SALESFORCE_CONSUMER_KEY)" \
		-p service/SALESFORCE_KEYSTORE_DATA="$(SALESFORCE_KEYSTORE_DATA)" \
		-p service/SALESFORCE_KEYSTORE_PASSWORD="$(SALESFORCE_KEYSTORE_PASSWORD)" \
		-p service/SALESFORCE_CERT_ALIAS="$(SALESFORCE_CERT_ALIAS)" \
		-p service/SALESFORCE_CERT_PASSWORD="$(SALESFORCE_CERT_PASSWORD)" \
		-n $(NAMESPACE)

oc_login:
	@oc login --token=${OC_LOGIN_TOKEN} --server=${OC_LOGIN_SERVER}
