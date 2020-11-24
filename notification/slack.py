import os
import requests
import json
import jinja2
import logging

logging = logging.getLogger(__name__)

class NotifySlack:
    """
    A class to interact with slack.

    ...

    Attributes
    ----------
    slack_token : str
        slack bot token to connect
    slack_channel : str
        slack channel to send notification on
    slack_icon_url : str
        small logo for slack block message.  
    notification_data: dict
        the dict containes all vars to create slack block message.

    Methods
    -------
    send_message(self):
        send the message to slack on the channel specified.
    """
    def __init__(self, slack_token, slack_channel, slack_icon_url, notification_description, **notfication_data):
        """
        Constructs all the necessary attributes for the notifyslack object.

        Parameters
        ----------
        slack_token : str
            slack bot token to connect
        slack_channel : str
            slack channel to send notification on
        slack_icon_url : str
            small logo for slack block message.  
        notification_description: str
            desctiption on slack message
        notification_data: dict
            the dict containes all vars to create slack block message.
        """
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.slack_icon_url = slack_icon_url
        self.notification_description = notification_description
        self.task = notfication_data['task']
        self.database_name = notfication_data['db']
        self.status = notfication_data['status']
        
    def send_message(self):
        """
        load the template and construct the slack block. send it to slack using chat.potmessage api.

        Returns
        -------
        slack api call result
        """
        loader = jinja2.FileSystemLoader('notification/templates')
        env = jinja2.Environment(loader=loader)
        env.filters['json'] = json.dumps
        template  = env.get_template('slack.json.j2')
        blocks = ( 
            template.render({
                'LOGO_URL' : self.slack_icon_url,
                'BACKUP_STATUS' : self.status,
                'BU' : self.notification_description,
                'HOSTNAME' : os.uname()[1],
                'TASK' : self.task,
                'DB_NAME' : self.database_name,
            })
        )           

        result = requests.post('https://slack.com/api/chat.postMessage', {
            'token': self.slack_token,
            'channel': self.slack_channel,
            'icon_url': self.slack_icon_url,
            'blocks': blocks if blocks else None
        }).json()
        
        return result

