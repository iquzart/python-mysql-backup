#!/usr/bin/python3
"""

 Description   :- MySQL or MariaDB backup tool.
 Author        :- Muhammed Iqbal <iquzart@hotmail.com>

"""
import os
import gzip
import time
import shlex
import logging
import datetime
import subprocess

from configparser import ConfigParser
from archive.blob_storage import AzureBlobStorage
from notification.slack import NotifySlack

    
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
    file_size_unit = backupConf.get('backup_file_size_unit') 
    
    time_formate = (time.strftime('%m%d%Y-%H%M%S'))

    if not os.path.exists(backup_dir):
        logging.debug('Creating backup directory {}'.format(backup_dir))
        os.makedirs(backup_dir)

    for db in db_list:
        
        dumpcmd = "mysqldump -u " + db_user + " -h " + db_host + " -P " + db_port + " -p" + db_password +" "+ db

        logging.debug('Creating backup for database: {}'.format(db))

        process = subprocess.run(shlex.split(dumpcmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = process.stdout    

        if  len(process.stderr) == 0:

            logging.debug('Creatting Zip file')

            file_name  = db + "-" + time_formate + ".sql.gz"
            dump_path = backup_dir + "/" + file_name
            with gzip.open(dump_path, 'wb') as f:
                f.write(data)
            
            # Calulate Size
            size = backup_file_size(dump_path, file_size_unit)
            logging.debug('Backup completed, the file size is: {}'.format(size))
            
            # Archive   
            if 'blob' in archive_type.lower():
                logging.debug('Updoading DB: {}'.format(db))
                azure_blob(file_name, dump_path, Config)
        
        
        else: 
            err = process.stderr.decode()
            logging.error(err)
            
            notification_slack(Config, db)




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
    
def notification_slack(Config, db):
    
    slackConf = Config["NOTIIFICAION_SLACK"]    

    slack_token = slackConf.get('slack_token')
    slack_channel = slackConf.get('slack_channel')
    slack_icon_url = slackConf.get('slack_icon_url')
    
    NotifySlack(slack_token, slack_channel, slack_icon_url, db).failure_message()

def main():
       
    # Read config.ini file
    Config = ConfigParser()
    Config.read("config_main.ini")

    logging.basicConfig(format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)


    db_backup(Config)

if __name__ == "__main__":
    main()



    
    