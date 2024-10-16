import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import logging
from utils import wait_for_page_load

def comment(driver: Chrome, comment):
    try:
        input = driver.find_element(
            By.XPATH, '//textarea[@aria-label="Add a comment…"]')
        input.click()
        input = driver.find_element(
            By.XPATH, '//textarea[@aria-label="Add a comment…"]')
        input.send_keys(comment)
        input.send_keys(Keys.ENTER)
        logging.info(f'Commented with {driver.email} : {comment}')
        return True
    except Exception as e:
        logging.error(f'Failed to comment with {driver.email}')
        return False


def like(driver: Chrome):
    try:
        like_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and @aria-label="Like" and @height="24"]'))
        )
        like_parent_div = like_btn.find_element(By.XPATH, './ancestor::div[@role="button"]')
        # click with js
        driver.execute_script("arguments[0].click();", like_parent_div)
        logging.info(f'Liked with {driver.email}')
        return True
    except Exception as e:
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and @aria-label="Unlike" and @height="24"]'))
            )
            logging.info(f'Already liked with {driver.email}')
            return True
        except:
            logging.error(f'Failed to like with {driver.email}')
            return False

def watch_story(driver: Chrome, username, from_profile=True):
    try:
        count = 0
        if from_profile: 
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//img[@alt="{username}\'s profile picture"]'))
            ).click()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.TAG_NAME, 'video')
        )
        logging.info(f'Watching story with {driver.email}')

        while True:
            try:
                vid_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'video'))
                )
            except Exception:
                break
            WebDriverWait(driver, 30).until(
                EC.text_to_be_present_in_element_attribute((By.TAG_NAME, 'video'), 'src', vid_elem.get_attribute('src'))
            )
            count += 1
            print('next story')
        logging.info(f'Stopped watching story with {driver.email} | count : {count}')
            # WebDriverWait(driver, 1000).until_not(
            #     lambda d: d.find_element(By.TAG_NAME, 'video')
            # )
            # change = check_dom_changes(driver, timeout=60)
            # if change:
            #     print('next story')
            #     count += 1
            # else:
            #     logging.info(f'Stopped watching story with {driver.email} | count : {count}')
    except Exception as e:
        logging.error(f'Failed to watch story with {driver.email}')

def work_on_story(driver: Chrome, links:list):
    logging.info(f'Working on stories with {driver.email}')
    count = 0
    for link in links:
        if not driver.current_url.startswith(link):
            driver.get(link)
            wait_for_page_load(driver)
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//div[text()="View story" and @role="button"]')
                    )
                ).click()
            except Exception:
                pass
        like(driver)
        current_url = driver.current_url
        WebDriverWait(driver, 10).until(
            EC.url_changes(current_url)
        )
        count += 1

    logging.info(f'Successfully worked on {count} stories with {driver.email}')

def follow(driver: Chrome):
    try:
        driver.find_element(By.XPATH, '//div[text()="Follow"]').click()
        logging.info(f'Followed with {driver.email}')
        return True
    except Exception as e:
        try:
            driver.find_element(By.XPATH, '//div[text()="Following" or text()="Requested"]')
            logging.info(f'Already followed with {driver.email}')
            return True
        except:
            logging.error(f'Failed to follow with {driver.email}')
            return False

def share(driver: Chrome, usernames):
    try:
        share_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[local-name()="svg" and @aria-label="Share"]'))
        )
        share_button.click()
        for username in usernames:
            input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Search" or @placeholder="Search..."]'))
            )
            input.click()
            input.send_keys(username)
            # user_parent_btn = user_btn.find_element(By.XPATH, 'ancestor::div[@role="button"]')
            user_parent_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//span[text()="{username}"]/ancestor::div[@role="button"]')
                )
            )
            # click with js
            user_parent_btn.click()
            # driver.execute("arguments[0].click();", user_parent_btn)
            time.sleep(1)
        send_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Send") and @role="button"]'))
        )
        send_btn.click()
        logging.info(f'Successfully shared with to {len(usernames)} users with {driver.email}')
        return True
    except Exception as e:
        logging.error(f'Failed to share with {driver.email}')
        return False
    