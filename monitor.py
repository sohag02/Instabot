import os
from utils import get_first_elem, login, wait_for_page_load, get_links, get_accounts, get_random_session
from actions import work_on_story
import logging
import random
import time
from driver import setup_driver
from config import Config
from process import process_batch, process_reels
from Scapper.scrape_followers import Scrapper, get_sessionid
import time
from datetime import datetime, timedelta
from instaloader import Instaloader, Profile
from multiprocessing import Process, Queue


logger = logging.getLogger(__name__)


def process_post(link, config: Config):
    logging.info(f'Processing post {link}')

    accounts = get_accounts(config.accounts or 1)
    if not accounts:
        return

    account_map = {
        link: accounts
    }
    total_likes, total_comments, total_shares, total_follows = 0, 0, 0, 0
    count_list = [total_likes, total_comments, total_shares, total_follows]

    for i in range(0, len(accounts), config.threads or 1):
        args = [(cred, [link], account_map)
                for cred in accounts[i:i + (config.threads or 1)]]

        process_batch(
            process_func=process_reels,
            args=args,
            config=config,
            count_list=count_list,
            story_links=[],
            size=config.threads or 1
        )


def process_story(config: Config):
    logging.info(f'Processing story')

    accounts = get_accounts(config.accounts or 1)
    if not accounts:
        return

    # for i
    #


def check_for_new_post(username):
    L = Instaloader()
    profile = Profile.from_username(L.context, username)

    posts = profile.get_posts()
    init_post = get_first_elem(posts)
    if init_post:
        init_post_id = init_post.shortcode
    else:
        init_post_id = None

    while True:
        print("fetching")
        posts = profile.get_posts()
        post = get_first_elem(posts)
        if post:
            if post.shortcode != init_post_id:
                return post.shortcode
        time.sleep(10)


def check_new_stories(username: str):
    print("check_new_stories")
    # Initialize instaloader instance
    L = Instaloader()

    # Load and convert the session
    session = get_random_session()
    if not session:
        logging.error('No session found. Please run login.py first.')
        return
    session_file = f'sessions/{session}'

    login(L, session_file)

    profile = Profile.from_username(L.context, username)

    # Fetch initial stories
    stories = L.get_stories(userids=[profile.userid])

    init_story = get_first_elem(stories)
    if init_story:
        for item in init_story.get_items():
            init_story_timestamp = item.date_utc
            init_story_id = item.mediaid
    else:
        init_story_timestamp = None
        init_story_id = None

    print(init_story_timestamp, 'init_story_timestamp')
    print(init_story_id, 'init_story_id')
    while True:
        new_stories = L.get_stories(userids=[profile.userid])

        new_story = get_first_elem(new_stories)
        if new_story:
            for item in new_story.get_items():
                new_story_timestamp = item.date_utc
                new_story_id = item.mediaid
                if new_story_id != init_story_id:
                    logging.info(f'New story found! Uploaded at {new_story_timestamp}')
                    return item.mediaid

        time.sleep(60*10)  # 10 minutes


def check_post(username, queue):
    while True:
        new_post_id = check_for_new_post(username)
        if new_post_id:
            queue.put(('post', new_post_id))
        time.sleep(60)  # Check every minute


def check_story(username, queue):
    while True:
        new_story_id = check_new_stories(username)
        if new_story_id:
            queue.put(('story', new_story_id))
        time.sleep(600)  # Check every 10 minutes


def monitor_content(username, config: Config):
    logging.info(f'Monitoring for posts and stories on {username}')

    last_post_id = None
    last_story_id = None

    queue = Queue()
    post_process = Process(target=check_post, args=(username, queue))
    story_process = Process(target=check_story, args=(username, queue))

    post_process.start()
    story_process.start()

    try:
        while True:
            item_type, item_id = queue.get()  # This will block until an item is available

            if item_type == 'post' and item_id != last_post_id:
                logging.info(f'New post detected: {item_id}')
                post_link = f'https://www.instagram.com/p/{item_id}/'
                process_post(post_link, config)
                last_post_id = item_id

            elif item_type == 'story' and item_id != last_story_id:
                logging.info(f'New story detected: {item_id}')
                process_story(config)
                last_story_id = item_id

    except KeyboardInterrupt:
        logging.info("Stopping monitoring...")
    finally:
        post_process.terminate()
        story_process.terminate()
        post_process.join()
        story_process.join()


def monitor(username, config: Config):
    print("start")
    sessions = os.listdir('sessions')

    driver = setup_driver(sessions[0].replace(
        '.pkl', ''), headless=config.headless)
    driver.get(f'https://www.instagram.com/{username}/')
    wait_for_page_load(driver)
    initial_links = get_links(driver, username, 2, log=False)

    session_id = get_sessionid(random.choice(sessions))

    scapper = Scrapper(sessionid=session_id)
    initial_stories = scapper.get_stories(username, 2)

    logging.info(f'Monitoring for posts and stories on {username}')

    last_story_check = datetime.now()
    story_check_interval = timedelta(minutes=10)

    while True:
        driver.refresh()
        wait_for_page_load(driver)
        time.sleep(2)
        # Check for new posts
        links = get_links(driver, username, 2)
        if links != initial_links:
            logging.info(f'New posts detected on {username}')
            print(links)
            initial_links = links
            process_post(link=links[0], config=config)

        # Check for new stories every 10 minutes
        if datetime.now() - last_story_check >= story_check_interval:
            stories = scapper.get_stories(username, 2)
            if stories != initial_stories:
                logging.info(f'New stories detected on {username}')
                print(stories)
                initial_stories = stories
                process_story(config=config)
            last_story_check = datetime.now()

        # Wait for 10 seconds before the next post check
        time.sleep(10)


if __name__ == '__main__':
    monitor_content('reyansh.yadav.546', Config())
    # process_post('https://www.instagram.com/p/DADCOcwyY_8/', Config())
