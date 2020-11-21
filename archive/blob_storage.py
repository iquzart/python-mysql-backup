import logging
from azure.storage.blob import BlobServiceClient

logging = logging.getLogger(__name__)

class AzureBlobStorage:
    def __init__(self, account_name, account_key, container_name, file_name):
    
        self.__blob_service_client = BlobServiceClient(account_url="https://"+account_name+".blob.core.windows.net", 
                            credential=account_key)
        
        self.__blob_client = self.__blob_service_client.get_blob_client(container=container_name, blob=file_name)        
        

    def upload(self, dump_path, file_name, container_name):
        
        logging.debug('Uploading the backup to Azure blob')
        
        with open(dump_path, "rb") as data:
           result = self.__blob_client.upload_blob(data, blob_type="BlockBlob")
           
        logging.debug("Successfully uploaded the backup '{}' to blob container '{}'".format(file_name, container_name))
        