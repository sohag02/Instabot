import logging
import time
from multiprocessing import Pool, Process, Queue

from instaloader import Instaloader, Profile

from actions import work_on_story
from config import Config
from driver import setup_driver
from process import get_proxy_batch, process_batch, process_reels
from utils import get_accounts, get_first_elem, login, wait_for_page_load, get_random_session

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

def story_process(acc, username, link, proxy):
    driver = setup_driver(acc, headless=Config.headless, proxy=proxy)
    driver.get(f'https://www.instagram.com/{username}')
    wait_for_page_load(driver)
    time.sleep(2)
    work_on_story(driver, [link])
    time.sleep(2)
    driver.quit()

def process_story(config: Config, link):
    logging.info('Processing story')

    accounts = get_accounts(config.accounts or 1)
    if not accounts:
        return

    for i in range(0, len(accounts), config.threads or 1):
        with Pool(config.threads or 1) as pool:
            accounts_batch = accounts[i:i + (config.threads or 1)]
            proxies_batch = get_proxy_batch(config, len(accounts_batch))
            args = [(acc, config.target_username, link, proxy) for acc, proxy in zip(accounts_batch, proxies_batch)]
            pool.starmap(story_process, args)


def check_for_new_post(username):
    L = Instaloader()
    profile = Profile.from_username(L.context, username)

    posts = profile.get_posts()
    if init_post := get_first_elem(posts):
        init_post_id = init_post.shortcode
    else:
        init_post_id = None

    while True:
        print("fetching")
        posts = profile.get_posts()
        post = get_first_elem(posts)
        if post and post.shortcode != init_post_id:
            return post.shortcode
        time.sleep(10*60)


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

    if init_story := get_first_elem(stories):
        for item in init_story.get_items():
            init_story_timestamp = item.date_utc
            init_story_id = item.mediaid
    else:
        init_story_timestamp = None
        init_story_id = None

    print(init_story_timestamp, 'init_story_timestamp')
    print(init_story_id, 'init_story_id')
    while True:
        print("story check")
        new_stories = L.get_stories(userids=[profile.userid])

        if new_story := get_first_elem(new_stories):
            print(new_story)
            for item in new_story.get_items():
                new_story_id = item.mediaid
                print(new_story_id)
                if new_story_id != init_story_id:
                    new_story_timestamp = item.date_utc
                    logging.info(f'New story found! Uploaded at {new_story_timestamp}')
                    return item.mediaid

        time.sleep(10)  # 10 minutes


def check_post(username, queue):
    while True:
        if new_post_id := check_for_new_post(username):
            queue.put(('post', new_post_id))
        time.sleep(60)  # Check every minute


def check_story(username, queue):
    while True:
        if new_story_id := check_new_stories(username):
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
                story_link = f'https://www.instagram.com/stories/{config.target_username}/{item_id}/'
                process_story(config, story_link)
                last_story_id = item_id

    except KeyboardInterrupt:
        logging.info("Stopping monitoring...")
    finally:
        post_process.terminate()
        story_process.terminate()
        post_process.join()
        story_process.join()



if __name__ == '__main__':
    monitor_content('reyansh.yadav.546', Config())
    # process_post('https://www.instagram.com/p/DADCOcwyY_8/', Config())
