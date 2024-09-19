import configparser
import logging
import random

logger = logging.getLogger(__name__)

class Content:
    def __init__(self, reels, photos, story):
        self.reels = reels
        self.photos = photos
        self.story = story

class Config:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Target
        self.target_username = self.config.get('target', 'username')
        self.range = self._get_optional_int('target', 'range')
        self.accounts = self._get_optional_int('target', 'accounts')
        self.threads = self._get_optional_int('target', 'threads')

        # Content
        self.content = Content(
            self.config.getboolean('content', 'reels'),
            self.config.getboolean('content', 'photos'),
            self.config.getboolean('content', 'story'),
        )

        # Options
        self.likes = self._get_int_from_range('options', 'likes')
        self.comments = self._get_int_from_range('options', 'comments')
        self.shares = self._get_int_from_range('options', 'shares')
        self.follows = self._get_int_from_range('options', 'follows')
        self.watch_time = self._get_int_from_range('options', 'watch_time')
        self.story_likes = self._get_int_from_range('options', 'story_likes')

        # Scrapper
        self.scrapper_mode = self.config.getboolean('scrapper', 'scrapper_mode')
        if self.scrapper_mode:
            self.target_username = self.config.get('scrapper', 'username').strip()
            self.range = self.config.getint('scrapper', 'range')

        # Monitor
        self.monitor_mode = self.config.getboolean('monitor', 'monitor_mode')
        if self.monitor_mode:
            self.target_username = self.config.get('monitor', 'username').strip()
            self.content.story = False
            self.follows = None

        # Proxy
        self.use_proxy = self.config.getboolean('proxy', 'use_proxy', fallback=False)
        if self.use_proxy:
            self.rotating_proxies = self.config.getboolean('proxy', 'rotating_proxies', fallback=False)
            if self.rotating_proxies:
                self.host = self.config.get('proxy', 'host', fallback=None)
                self.port = self.config.get('proxy', 'port', fallback=None)
                self.proxy_username = self.config.get('proxy', 'username', fallback=None)
                self.proxy_password = self.config.get('proxy', 'password', fallback=None)
            else:
                self.proxy_file = self.config.get('proxy', 'proxy_file', fallback=None)

        # Settings
        self.headless = self.config.getboolean('settings', 'headless', fallback=False)


    def _get_optional_int(self, section, option):
        """Returns the value as an integer if present and non-zero, or None if empty or zero."""
        value = self.config.get(section, option, fallback=None)
        return int(value) if value and int(value) != 0 else None

    def _get_int_from_range(self, section, option):
        """Returns the value as an integer if present and non-zero, or None if empty or zero."""
        value = self.config.get(section, option, fallback=None)
        if value:
            try:
                start, end = value.split('-')
                return random.randint(int(start), int(end))
            except ValueError:
                if value == '0':
                    return None
                logger.error(f"Invalid range value for {option}: {value}")
                exit()

        else:
            return None


    def validate(self):
        """Validates all the config fields at once."""
        if self.target_username and not self.range:
            logger.error("Target username is set but range is not. Please set the range.")
            exit()

        self.likes = self.likes * self.range
        self.comments = self.comments * self.range
        self.shares = self.shares * self.range

        # keys = self.search_keywords.split(',')
        # self.search_keywords = [key.strip() for key in keys]

if __name__ == "__main__":
    config = Config()
    # config.display
    print(config.search_keywords)
