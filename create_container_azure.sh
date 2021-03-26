AZURE_STORAGE_ACCOUNT=storageaccountclima8442
RESOURCE_GROUP=climate-hackathon-machine-learning-space
SHARE_NAME=mapdata
STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $AZURE_STORAGE_ACCOUNT --query "[0].value" --output tsv)

az container create \
    --resource-group $RESOURCE_GROUP \
    --name hacktheclimate \
    --image hacktheclimate.azurecr.io/hacktheclimate:1 \
    --dns-name-label methaneapp \
    --region switzerlandnorth \
    --ports 80 \
    --azure-file-volume-account-name $AZURE_STORAGE_ACCOUNT \
    --azure-file-volume-account-key "$STORAGE_KEY" \
    --azure-file-volume-share-name $SHARE_NAME \
    --azure-file-volume-mount-path /mount/data
