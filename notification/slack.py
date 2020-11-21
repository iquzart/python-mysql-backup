import requests
import json
import jinja2
import logging

logging = logging.getLogger(__name__)

class NotifySlack:
    def __init__(self, slack_token, slack_channel, slack_icon_url, db):

        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.slack_icon_url = slack_icon_url
        self.db = db
        
    def failure_message(self):

        loader = jinja2.FileSystemLoader('notification/templates')
        env = jinja2.Environment(loader=loader)
        env.filters['json'] = json.dumps
        template  = env.get_template('slack.json.j2')
        blocks = ( 
            template.render({
                'LOGO_URL' : self.slack_icon_url,
                'BACKUP_STATUS' : 'Backup Failed',
                'COMPANY_NAME' : 'Some Test Company',
                'HOSTNAME' : 'LXORDEVDBV01',
                'FAILED_ON' : 'Backup',
                'DB_NAME' : self.db,
            })
        )           

        result = requests.post('https://slack.com/api/chat.postMessage', {
            'token': self.slack_token,
            'channel': self.slack_channel,
            'icon_url': self.slack_icon_url,
            'blocks': blocks if blocks else None
        }).json()
        
        if result['ok']:
            logging.debug('sent a notification to {} channel'.format(self.slack_channel) )
        else:
            logging.debug("Failed sending notification, Error message - '{}'".format(result['error']))

