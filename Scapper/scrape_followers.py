import os
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import pickle
from datetime import datetime
import logging
import requests
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)-5s - %(message)s')

logging.getLogger("instagrapi").setLevel(logging.ERROR)

def convert_cookies(selenium_cookies):
    """Converts selenium cookies to instaloader cookies"""
    session = requests.Session()
    for cookie in selenium_cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    return session.cookies.get_dict()

class Scrapper(Client):

    def __init__(self, username=None, password=None, sessionid=None):
        super().__init__()
        # logging.getLogger("instagrapi").setLevel(logging.ERROR)
        if username and password:
            self.login(username, password)
        elif sessionid:
            self.login_by_sessionid(sessionid)
        else:
            raise ValueError('Please provide either username and password or sessionid')
        
    def login_from_session(self, session_file):
        with open(f'sessions/{session_file}', 'rb') as f:
            selenium_cookies = pickle.load(f)
        cookies = convert_cookies(selenium_cookies)
        print(cookies)
        # self.login_by_sessionid(cookies['sessionid'])
        # self.private = session
        self.private.cookies.update(cookies)

    def get_followers(self, username:str, range:int):
        logging.info(f'Getting user infor for {username}...')
        user = self.user_info_by_username(username)
        logging.info(f'Scraping followers for {username}...')
        followers = self.user_followers(user.pk, amount=range)
        user_followers = [followers[follower].username for follower in followers]
        logging.info(f'Scrapped {len(user_followers)} followers Successfully.')
        return user_followers

    def share_reel(self, reel_id, user_id_list):
        return self.direct_media_share(
            reel_id,
            user_id_list,
            media_type='video',
        )

    def generate_user_id_list(self, usernames):
        user_id_list = []
        for username in usernames:
            user = self.user_info_by_username(username)
            user_id_list.append(user.pk)
        return user_id_list

    def get_stories(self, username, range):
        user = self.user_info_by_username(username)
        user_id = user.pk
        logging.info(f'Scraping stories for {username}...')
        stories = self.user_stories(user_id, amount=range)
        user_stories = [story.pk for story in stories]
        logging.info(f'Scrapped {len(user_stories)} stories Successfully.')
        return user_stories

def get_sessionid(session_file):
    with open(f'sessions/{session_file}', 'rb') as f:
        cookies = pickle.load(f)
        # cookies_dict = {}
        for cookie in cookies:
            if cookie['name'] == 'sessionid':
                return cookie['value']


def get_first_key_value(input_dict):
  if not input_dict:
    return None  # Handle empty dictionary case

  first_key = next(iter(input_dict))  # Get the first key using an iterator
  return input_dict[first_key]  # Return the value associated with the first key

if __name__ == '__main__':
    config = Config()
    logging.info(f'Starting scrapper for username : {config.username}')

    sessions = os.listdir('sessions')
    if not sessions:
        logging.error('No sessions found in sessions folder')
        exit()

    session = random.choice(sessions)
    logging.info(f'Using session : {session}')

    session_id = get_sessionid(session)

    scrapper = Scrapper(sessionid=session_id)
    logging.info(f'Logged in successfully as {scrapper.username}')

    logging.info('Scrapping followers...')
    try:
        followers = scrapper.get_followers(config.username, config.range)
    except LoginRequired:
        logging.error(f'Session {session} has expired or is suspended')
        exit()
    except Exception as e:
        logging.error('An error occurred while scrapping followers')
        exit()

    logging.info('Saving followers...')
    with open(f'{config.username}.txt', 'w') as f:
        f.write('\n'.join(followers))
    logging.info(f'Successfully saved followers to {config.username}.txt')
