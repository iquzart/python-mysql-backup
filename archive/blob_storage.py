import logging
from azure.storage.blob import BlobServiceClient

logging = logging.getLogger(__name__)

class AzureBlobStorage:
    def __init__(self, account_name, account_key, container_name, file_name, dump_path):
    
        self.container_name = container_name
        self.file_name = file_name
        self.dump_path = dump_path
        
        self.__blob_service_client = BlobServiceClient(account_url="https://"+account_name+".blob.core.windows.net", 
                            credential=account_key)
        
        self.__blob_client = self.__blob_service_client.get_blob_client(container=self.container_name, blob=self.file_name)        
        

    def upload(self):
        
        logging.debug("Uploading the backup file - '{}'".format(self.dump_path))
        
        with open(self.dump_path, "rb") as data:
           result = self.__blob_client.upload_blob(data, blob_type="BlockBlob")
           return result
        
        