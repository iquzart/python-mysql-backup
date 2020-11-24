#!/usr/bin/python3
"""

 Description   :- MySQL or MariaDB backup script.
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

    
def db_backup(dbInfo, backupConf):
    '''
    take mysql or mariadb dump with gzip compression.

            Parameters:
                    dbInfo (sectionproxy): database details from configparser
                    backupConf (sectionproxy): backup config details from configparser

            Returns:
                    res (list): database dump result in a list of dictionaries.
    '''
       
    db_list = dbInfo.get('db_name').split(',')
    db_user = dbInfo.get('username')
    db_password = dbInfo.get('password')
    db_host = dbInfo.get('db_host')
    db_port = dbInfo.get('db_port')
    backup_dir = backupConf.get('backup_dir')
    file_size_unit = backupConf.get('backup_file_size_unit')
    time_formate = (time.strftime('%m%d%Y-%H%M%S'))

    if not os.path.exists(backup_dir):
        logging.debug("Creating backup directory '{}'".format(backup_dir))
        os.makedirs(backup_dir)
    
    res = []
    for db in db_list:
        dumpcmd = "mysqldump -u " + db_user + " -h " + db_host + " -P " + db_port + " -p" + db_password +" "+ db
        logging.debug("Creating backup for database: '{}'".format(db))
        
        # data to variable
        process = subprocess.run(shlex.split(dumpcmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = process.stdout    
        if  len(process.stderr) == 0:

            # Write data to file and compress it
            file_name  = db + "-" + time_formate + ".sql.gz"
            dump_path = backup_dir + "/" + file_name
            with gzip.open(dump_path, 'wb') as f:
                f.write(data)
            
            # Calulate Size
            size = backup_file_size(dump_path, file_size_unit)
            logging.debug('Backup completed')
            logging.debug("Backup file: '{}' - Size: '{}'".format(dump_path,size))
            
            res_data = {db: {'file_name': file_name,'dump_path': dump_path,'backup_status': 'Success'}}
            res.append(res_data)                
        else: 
            res_data = {db: {'file_name': None,'dump_path': None,'backup_status': 'Failed'}}
            res.append(res_data)
            err = process.stderr.decode()
            logging.error(err)
    return res


def backup_file_size(dump_path, file_size_unit):
    '''
    calculate dump file size. return the value with unit.

            Parameters:
                    dump_path (str): database dump path
                    file_size_unit (str): file size unit

            Returns:
                    size (str): dump file size with unit.
    '''
       
    size = os.path.getsize(dump_path) 
    if file_size_unit == "KB":
        return str(round(size / 1024, 3)) + file_size_unit
    elif file_size_unit == "MB":
        return str(round(size / (1024 * 1024), 3)) + file_size_unit
    elif file_size_unit == "GB":
        return str(round(size / (1024 * 1024 * 1024), 3)) + file_size_unit
    else:
        return str(size) + ' bytes'

def expire_local_backup(backupConf):
    '''
    delete the files older than specified retention date.
    '''
    now = time.time()
    backup_dir = backupConf.get('backup_dir')
    retention_days = (backupConf.get('retention_days'))
    logging.debug("Finding backup stored older than '{}' day(s)".format(retention_days))
    
    for file in os.listdir(backup_dir):
        if os.stat(os.path.join(backup_dir,file)).st_mtime < now - float(retention_days) * 86400:
            logging.debug('Deleting local backup file: {}'. format(file))
            os.remove(os.path.join(backup_dir, file))
    

def azure_blob(Config, file_name, dump_path, db):
    """
    upload file to azure blob container.

            Parameters:
                    Config (sectionproxy): database details from configparser
                    file_name (str): local file name, to set as blob name
                    dump_path (str): local backup dump file path to upload
                    db (str): backup config details from configparser
    """    
    azureBlobConf = Config["ARCHIVE_AZURE"]    
    account_name = azureBlobConf.get('account_name')
    account_key = azureBlobConf.get('account_key')
    container_name = azureBlobConf.get('container_name')    
    
    logging.debug('Initiating archive to Azure blob storage')
    logging.debug("Uploading the backup file - '{}'".format(dump_path))
    
    result = AzureBlobStorage(
        account_name, 
        account_key, 
        container_name, 
        file_name, 
        dump_path).upload()

    if result == True:
        logging.debug("Successfully uploaded the backup '{}' to blob container '{}'".format(file_name, container_name))
    else:
        logging.error('Upload Failed..!')
        logging.error('Error Message: {}'.format(result))
        notification_slack(Config, db=db, task='Archive', status='Failed')
        

def notification_slack(Config, **notfication_data):
    """
    send notification to slack.

            Parameters:
                    Config (sectionproxy): database details from configparser
                    notfication_data (dict): all vars to create slack block message.
    """      
    slackConf = Config["NOTIIFICAION_SLACK"]
    slack_token = slackConf.get('slack_token')
    slack_channel = slackConf.get('slack_channel')
    slack_icon_url = slackConf.get('slack_icon_url')
    notification_description = slackConf.get('notification_description')
       
    result = NotifySlack(
                slack_token, 
                slack_channel, 
                slack_icon_url, 
                notification_description,
                **notfication_data).send_message()
    
    if result['ok']:
        logging.debug('Sent a notification to {} channel'.format(slack_channel) )
    else:
        logging.debug("Failed sending notification, Error message - '{}'".format(result['error']))

def main():
    
    # Read config.ini file
    Config = ConfigParser()
    Config.read("config_main.ini")
    
    dbInfo = Config["DBINFO"]
    backupConf = Config["BACKUP_CONF"]

    archive_type = backupConf.get('archive_type')
    notification_channel = backupConf.get('notification_channel')  

    logging.basicConfig(format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)
    
    # Initiate Backup
    backup_results = db_backup(dbInfo, backupConf)
    
    # Action based on Backup result   
    for d in backup_results:
        for db, properties in d.items():
            file_name = properties['file_name']
            dump_path = properties['dump_path']
            backup_status = properties['backup_status']
            
            if backup_status == 'Success':
                # Archive to Azure Blob
                if 'blob' in archive_type.lower():
                    azure_blob(Config, file_name, dump_path, db)  
                
                # Delete local Backup based on retention config
                expire_local_backup(backupConf)       
                
            else:
                # Slack Notification on Backup Failure
                if 'slack' in notification_channel.lower():    
                    notification_slack(Config, db=db, task='Backup', status=backup_status)

if __name__ == "__main__":
    main()



    
    