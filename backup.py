#!/usr/bin/python3
import os
import time
import datetime
from configparser import ConfigParser


# Read config.ini file
Config = ConfigParser()
Config.read("config.ini")
dbInfo = Config["DBINFO"]
backupInfo = Config["BACKUPINFO"]

db_list = dbInfo.get('db_name').split(',')
db_user = dbInfo.get('username')
db_password = dbInfo.get('password')
db_host = dbInfo.get('db_host')
db_port = dbInfo.get('db_port')

backup_dir = backupInfo.get('backup_dir')
archive_type = backupInfo.get('archive_type')
notification_channel = backupInfo.get('notification_channel')
success_notification = backupInfo.get('Success_notification')

time_formate = (time.strftime('%m%d%Y-%H%M%S'))

    
def db_backup():

    if not os.path.exists(backup_dir):
        print('creating backup directory {}'.format(backup_dir))
        os.makedirs(backup_dir)

    for db in db_list:
        dump_filename = backup_dir + "/" + db + "-" + time_formate + ".sql.gz"

        dumpcmd = "mysqldump -u " + db_user + " -h " + db_host + " -P " + db_port + " -p" + db_password +" "+ db + " | gzip >" + dump_filename  

        print('creating backup for database: {}'.format(db))
        os.system(dumpcmd)	
        size = backup_file_size(dump_filename)
        
        print('backup completed, the file size is: {}'.format(size))

def backup_file_size(dump_filename, unit=backupInfo.get('backup_file_size_unit')):

    size = os.path.getsize(dump_filename) 
    if unit == "KB":
        return str(round(size / 1024, 3)) + unit
    elif unit == "MB":
        return str(round(size / (1024 * 1024), 3)) + unit
    elif unit == "GB":
        return str(round(size / (1024 * 1024 * 1024), 3)) + unit
    else:
        return str(size) + ' bytes'
         
db_backup()