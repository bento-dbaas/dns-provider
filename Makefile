setup:
	@rm -rf venv
	@test -f venv/bin/activate || virtualenv -p $(shell which python3) venv
	@. venv/bin/activate ;\
	pip3 install -r requirements.txt
run:
	@. venv/bin/activate; \
	export FLASK_DEBUG=1; \
	export FLASK_APP=./dns_provider/main.py; \
	python -m flask run
test:
		@. venv/bin/activate; \
		export APP_SETTINGS=dns_provider.config.TestingConfig; \
		pytest
setup_docker:
	@docker build -t dns_provider .
run_docker:
	@docker run -p 8000:8000 dns_provider
deploy_dev:
	@tsuru app-deploy -a dns-provider-dev .
deploy_prod:
	@tsuru app-deploy -a dns-provider .
run_local:
	export FLASK_APP=./dns_provider/main.py; python -m flask run
