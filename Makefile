
install-functions-mac:
	brew tap azure/functions; \
	brew install azure-functions-core-tools@3

create-env-for-funcs:
	python -m venv .venv; \
	source .venv/bin/activate; \
	pip install -r requirements-func.txt

publish-func:
	func azure functionapp publish loadhotspots
