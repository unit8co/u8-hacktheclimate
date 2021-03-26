export AZURE_STORAGE_ACCOUNT=storageaccountclima8442
RESOURCE_GROUP=climate-hackathon-machine-learning-space
functionAppName=loadhotspots
region=westeurope
pythonVersion=3.7
shareName=mapdata
shareId=mapdata$RANDOM
mountPath=/mounted

export AZURE_STORAGE_KEY=$(az storage account keys list -g $RESOURCE_GROUP -n $AZURE_STORAGE_ACCOUNT --query '[0].value' -o tsv)

az functionapp create \
  --name $functionAppName \
  --storage-account $AZURE_STORAGE_ACCOUNT \
  --consumption-plan-location $region \
  --resource-group $RESOURCE_GROUP \
  --os-type Linux \
  --runtime python \
  --runtime-version $pythonVersion \
  --functions-version 2

az webapp config storage-account add \
  --resource-group $RESOURCE_GROUP \
  --name $functionAppName \
  --custom-id $shareId \
  --storage-type AzureFiles \
  --share-name $shareName \
  --account-name $AZURE_STORAGE_ACCOUNT \
  --mount-path $mountPath \
  --access-key "$AZURE_STORAGE_KEY"

az webapp config storage-account list \
  --resource-group $RESOURCE_GROUP \
  --name $functionAppName
