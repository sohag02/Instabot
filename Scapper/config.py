from configparser import ConfigParser
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_file='config.ini'):
        self.config = ConfigParser()
        self.config.read(config_file)

        # Scrapper
        self.username = self.config.get('scrapper', 'username', fallback=None)
        self.range = self.config.getint('scrapper', 'range', fallback=0)

        # Messenger
        self.accounts = self.config.getint('messenger', 'accounts', fallback=0)
        self.msg_file = self.config.get('messenger', 'msg_file', fallback=None)
        self.username_file = self.config.get('messenger', 'username_file', fallback=None)

        # Settings
        self.headless = self.config.get('settings', 'headless', fallback=None)
        