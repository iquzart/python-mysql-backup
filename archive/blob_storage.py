import logging
import sys
from azure.storage.blob import BlobServiceClient

logging = logging.getLogger(__name__)

class AzureBlobStorage:
    """
    A class to interact with azure blob.

    ...

    Attributes
    ----------
    account_name : str
        azure storage account name
    account_key : str
        azure storage account access key
    file_name : str
        local file name to set as blob name  
    dump_path: str
        local file path to create blob from.

    Methods
    -------
    upload(self):
        upload block blob to azure blob container.
    """
    def __init__(self, account_name, account_key, container_name, file_name, dump_path):
        """
        Constructs all the necessary attributes for the azureblobstorage object.

        Parameters
        ----------
        account_name : str
            azure storage account name
        account_key : str
            azure storage account access key
        file_name : str
            local file name to set as blob name  
        dump_path: str
            local file path to create blob from.

        """    
        self.container_name = container_name
        self.file_name = file_name
        self.dump_path = dump_path
        
        self.__blob_service_client = BlobServiceClient(account_url="https://"+account_name+".blob.core.windows.net", 
                            credential=account_key)
        
        self.__blob_client = self.__blob_service_client.get_blob_client(container=self.container_name, blob=self.file_name)        
        

    def upload(self):
        """
        upload file to azure blob container.

        Returns
        -------
        return success as 'true' failure with error message
        """
        try:
            with open(self.dump_path, "rb") as data:
                self.__blob_client.upload_blob(data, blob_type="BlockBlob")
                return True
        except:
            return sys.exc_info()[1]
        