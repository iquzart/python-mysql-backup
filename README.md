# MySQL Backup

MySQL or MariaDB backup script.


Features
---------

1. Multiple DB support
2. Backup Archive to Azure Blob Storage
3. Notification - Slack, Email, Teams


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

ToDo
-----

```
1. Notification (Slack, Email, Teams)
2. Logging
```

License
-------

MIT

Author Information
------------------

Muhammed Iqbal <iquzart@hotmail.com>