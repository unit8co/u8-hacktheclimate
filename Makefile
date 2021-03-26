login:
	az login; \
	az account set --subscription "Pass Azure - Sponsorship"; \
	az acr login --name hacktheclimate

publish:
	echo Did you make login?; \
	docker build . -t hacktheclimate.azurecr.io/hacktheclimate:1; \
	docker push hacktheclimate.azurecr.io/hacktheclimate:1; \
	az container restart --name hacktheclimate --resource-group climate-hackathon-machine-learning-space

install-functions-mac:
	brew tap azure/functions; \
	brew install azure-functions-core-tools@3

create-env-for-funcs:
	python -m venv .venv; \
	source .venv/bin/activate; \
	pip install -r requirements-func.txt

publish-func:
	func azure functionapp publish loadhotspots
