from instagrapi import Client
import pickle
from datetime import datetime
import logging
# from import convert_cookies

# from .utils import convert_cookies

logger = logging.getLogger(__name__)

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

    def get_followers(self, username, range):
        logging.info(f'Scraping followers for {username}...')
        user = self.user_info_by_username(username)
        followers = self.user_followers(user.pk, amount=range)
        user_followers = []
        for follower in followers:
            user_followers.append(followers[follower].username)
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
        user_stories = []
        for story in stories:
            user_stories.append(story.pk)
        logging.info(f'Scrapped {len(user_stories)} stories Successfully.')
        return user_stories

def get_sessionid(session_file):
    with open(f'sessions/{session_file}', 'rb') as f:
        cookies = pickle.load(f)
        # cookies_dict = {}
        for cookie in cookies:
            if cookie['name'] == 'sessionid':
                sessionid = cookie['value']
                # print(sessionid)
                return sessionid


def get_first_key_value(input_dict):
  if not input_dict:
    return None  # Handle empty dictionary case

  first_key = next(iter(input_dict))  # Get the first key using an iterator
  return input_dict[first_key]  # Return the value associated with the first key


def get_last_seen(user_id):
    data={
        "request_data": f"[{int(user_id)}]",
        "_uuid": cl.uuid,
        "subscriptions_off": "false",
    }

    res = cl.private_request('direct_v2/get_presence/', data=cl.with_default_data(data))
    print(res)
    last_activity = get_first_key_value(res['user_presence'])['last_activity_at_ms']
    return last_activity/1000

def get_time_since_last_seen(last_seen):
    current_time = datetime.now().timestamp()
    print(f"Current Time: {datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Last Seen: {datetime.fromtimestamp(last_seen).strftime('%Y-%m-%d %H:%M:%S')}")
    time_since_last_seen = current_time - float(last_seen)
    return time_since_last_seen

if __name__ == '__main__':
    session_id = get_sessionid('jessica.brown.202121@gmail.com.pkl')
    # scrapper = Scrapper(username='amie7edssi2', password='Hardik45')
    scrapper = Scrapper(sessionid=session_id)
    # print(scrapper.private.cookies)
    # scrapper.login_from_session('david.lee.198565@gmail.com.pkl')
    # print(scrapper.username)
    # print(scrapper.private.cookies)
    # scrapper.get_timeline_feed()
    # scrapper.private_request
    # user_id_list = scrapper.generate_user_id_list(['itss.s.j'])
    # print(user_id_list)
    # s = scrapper.share_reel('C_cPFf_Pjre', user_id_list)
    # print(s)
    user = scrapper.user_info_by_username('maisamayhoon')
    # st = scrapper.get_stories(user.pk, 2)
    f = scrapper.get_followers('maisamayhoon', 20)

    print(f)
