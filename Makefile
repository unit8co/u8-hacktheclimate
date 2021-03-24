login:
	az login; \
	az account set --subscription "Pass Azure - Sponsorship"; \
	az acr login --name hacktheclimate

publish: login
	docker build . -t hacktheclimate.azurecr.io/hacktheclimate:1; \
	docker push hacktheclimate.azurecr.io/hacktheclimate:1; \
	az container restart --name hacktheclimate --resource-group climate-hackathon-machine-learning-space