#!/usr/bin/python3
"""

 Description   :- MySQL or MariaDB backup tool.
 Author        :- Muhammed Iqbal <iquzart@hotmail.com>

"""
import os
import time
import datetime
from configparser import ConfigParser
from archive.blob_storage import AzureBlobStorage

    
def db_backup(Config):
    
    dbInfo = Config["DBINFO"]
    backupConf = Config["BACKUP_CONF"]
    
    db_list = dbInfo.get('db_name').split(',')
    db_user = dbInfo.get('username')
    db_password = dbInfo.get('password')
    db_host = dbInfo.get('db_host')
    db_port = dbInfo.get('db_port')
    
    backup_dir = backupConf.get('backup_dir')
    archive_type = backupConf.get('archive_type')
    notification_channel = backupConf.get('notification_channel')
    success_notification = backupConf.get('success_notification')
    compress_backup = backupConf.get('compress_backup')   
    file_size_unit = backupConf.get('backup_file_size_unit') 
    
    time_formate = (time.strftime('%m%d%Y-%H%M%S'))

    if not os.path.exists(backup_dir):
        print('Creating backup directory {}'.format(backup_dir))
        os.makedirs(backup_dir)

    for db in db_list:
        
        if (compress_backup == 'True' or compress_backup == 'on'):
            file_name  = db + "-" + time_formate + ".sql.gz"
            dump_path = backup_dir + "/" + file_name
            dumpcmd = "mysqldump -u " + db_user + " -h " + db_host + " -P " + db_port + " -p" + db_password +" "+ db + " | gzip >" + dump_path  
        else:           
            file_name  = db + "-" + time_formate + ".sql"
            dump_path = backup_dir + "/" + file_name
            dumpcmd = "mysqldump -u " + db_user + " -h " + db_host + " -P " + db_port + " -p" + db_password +" "+ db + ">" + dump_path              
            
        print('Creating backup for database: {}'.format(db))

        os.system(dumpcmd)	
        size = backup_file_size(dump_path, file_size_unit)
        print('Backup completed, the file size is: {}'.format(size))
        
        # Archive        
        if 'blob' in archive_type.lower():
            azure_blob(file_name, dump_path, Config)

def backup_file_size(dump_path, file_size_unit):

    size = os.path.getsize(dump_path) 
    if file_size_unit == "KB":
        return str(round(size / 1024, 3)) + file_size_unit
    elif file_size_unit == "MB":
        return str(round(size / (1024 * 1024), 3)) + file_size_unit
    elif file_size_unit == "GB":
        return str(round(size / (1024 * 1024 * 1024), 3)) + file_size_unit
    else:
        return str(size) + ' bytes'

def azure_blob(file_name, dump_path, Config):
    
    azureBlobConf = Config["ARCHIVE_AZURE"]    
    
    account_name = azureBlobConf.get('account_name')
    account_key = azureBlobConf.get('account_key')
    container_name = azureBlobConf.get('container_name')    
    
    AzureBlobStorage(account_name, account_key, container_name, file_name).upload(dump_path, file_name, container_name)
    


def main():
    # Read config.ini file
    Config = ConfigParser()
    Config.read("config_main.ini")

    db_backup(Config)

if __name__ == "__main__":
    main()



    
    