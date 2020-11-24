# MySQL Backup

MySQL or MariaDB backup script.


Features
---------

1. Configurable 
2. Multiple DB support
3. Backup Archive to Azure Blob Storage
4. Notification - Slack


Configuration
--------------

Variable Group: DBINFO

| Variable | Description | sample |
| --- | --- | ---|
| db_name |  Database Names, comma-separated values | demo,demo1,demo2   |
| db_host |  Database Host Name   |    |
| db_port |  Database Host Port   |    |
| username |  Database Username   |    |
| password |  Database Password   |    |


Variable Group: BACKUP_CONF

| Variable | Description | sample |
| --- | --- | ---|
| backup_dir  |  Local Backup Directory   |  /tmp/mysql-backup  |
| compress_backup  | Compress Backup (on or off, True or False)    |  True  |
| archive_type  |  Backup Archive Types    |  Blob  |
| notification_channel  |  Backup notification channels   |  Slack, Email, Teams  |
| success_notification  |  Enabled backup success notification   |  False  |
| backup_file_size_unit  |  Backup file size in KB, MB, GB, None(bytes)   |  MB  |


Variable Group: ARCHIVE_AZURE

| Variable | Description | sample |
| --- | --- | ---|
|  account_name   |  Storage Account Name   |  demostgacc  |
|  account_key   |   Storage Account key  |    |
|  container_name   |  Blob container Name   | mysqlbackup   |


Variable Group: NOTIIFICAION_SLACK

| Variable | Description | sample |
| --- | --- | ---|
| slack_token  | Slack BOT Token |  | 
| slack_channel | Slack Notification Channel | |
| slack_icon_url | Company or Application | |
| notification_description | Application or Business Unit Name | |


ToDo
-----


1. Notification 
    1. ~~Slack~~
    2. Email
    3. Teams
2. Archive location
    1. AWS s3

License
-------

MIT

Author Information
------------------

Muhammed Iqbal <iquzart@hotmail.com>