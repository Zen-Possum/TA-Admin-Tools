# ======================================================================================================================
# HermesBot.py automates sending the same message to multiple users on chess.com, which can be specified in list or CSV
# format. It requires an up-to-date chrome driver (https://chromedriver.chromium.org/downloads) and valid Chess.com
# login credentials. Written by ZenPossum :)
# ======================================================================================================================

from selenium import common
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from Credentials import username, password

# 1. Create a separate file called Credentials.py and copy the following, replacing the bold text with your login
# credentials.
# username = 'USERNAME_HERE'
# password = 'PASSWORD_HERE'

# 2. Input the list of users to send the message to here, either using a CSV with a 'username' column or manually
file_name = ''  # 'FILE_NAME_HERE.csv'. Leave as '' or None to use the manual list
if file_name:
    df = pd.read_csv(file_name)
    list_of_names = list(df['username'])
else:
    list_of_names = []
N = len(list_of_names)

options = Options()
options.add_argument('user-agent=TA')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://www.chess.com/messages/compose')


def login():
    # LOGIN logs in using the given credentials
    login_boxes = driver.find_elements(By.CLASS_NAME, 'cc-input-component')
    login_boxes[1].send_keys(username)
    login_boxes[2].send_keys(password)
    driver.find_element(By.ID, 'login').click()


def fill_recipient(name):
    # FILL_RECIPIENT fills the message recipient box with a given username
    address_box = driver.find_elements(By.CLASS_NAME, 'ui_v5-input-component')
    address_box[3].clear()
    address_box[3].send_keys(name)
    name_popup = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CLASS_NAME, 'username-search-autocomplete-field')))
    name_popup.click()
    time.sleep(1)


def write_plain_text(text):
    # WRITE_PLAIN_TEXT writes plain text to the message box
    driver.find_element(By.ID, 'tinymce').send_keys(text)


def write_bold_text(text):
    # WRITE_PLAIN_TEXT writes bold text to the message box
    driver.find_element(By.ID, 'tinymce').send_keys(Keys.CONTROL + 'b')
    driver.find_element(By.ID, 'tinymce').send_keys(text)
    driver.find_element(By.ID, 'tinymce').send_keys(Keys.CONTROL + 'b')


def write_italics_text(text):
    # WRITE_PLAIN_TEXT writes italics text to the message box
    driver.find_element(By.ID, 'tinymce').send_keys(Keys.CONTROL + 'i')
    driver.find_element(By.ID, 'tinymce').send_keys(text)
    driver.find_element(By.ID, 'tinymce').send_keys(Keys.CONTROL + 'i')


def insert_image(url):
    # INSERT_IMAGE inserts the image with the given address into the message
    driver.switch_to.default_content()  # Switch back to default frame
    driver.find_element(By.XPATH, '//button[@title="Insert Image"]').click()
    time.sleep(1)
    image_menu_frame = driver.find_element(By.XPATH, "//iframe[contains(@src, '/tinymce/imageuploader')]")
    driver.switch_to.frame(image_menu_frame)
    time.sleep(1)
    driver.find_element(By.ID, 'image-uploader-external-link').send_keys(url)
    driver.find_element(By.CLASS_NAME, 'cc-button-primary').click()
    driver.switch_to.default_content()
    text_input_frame = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.ID, 'mce_0_ifr')))
    driver.switch_to.frame(text_input_frame)


def send_message(name, delay=12):
    # SEND_MESSAGE defines the message sequence
    try:
        driver.switch_to.frame('mce_0_ifr')  # Switch frames for rich text editor
        # MESSAGE SEQUENCE HERE
        insert_image('https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/Kookaburrra/phpeGUx85.gif')
        write_bold_text('\nTeam Australia World League Round 1 2025 against the Czech Republic.')
        write_plain_text('\nWe need everyone available to play. This is our most important '
                         'league!\nhttps://www.chess.com/club/matches/team-australia/1723007')
        driver.switch_to.default_content()  # Switch back
        driver.find_element(By.ID, 'message-submit').click()  # Send message
        print(f'Sent message to {name} ({n} of {N})')
        time.sleep(delay)
    except [common.exceptions.ElementNotInteractableException, common.exceptions.NoSuchElementException]:
        # If user cannot be messaged
        print(f'Unable to message {name} ({n} of {N}).')
        blocked_users.append(name)


def new_message():
    # NEW_MESSAGE prepares the page to compose a new message
    driver.find_element(By.CLASS_NAME, 'message-list-search-compose').click()
    time.sleep(1)


if __name__ == '__main__':
    # Log in to the messaging portal
    login()
    print('Logged in.')
    time.sleep(1)

    # Wait for page to load before sending messages
    print('Loading message page...')
    while driver.find_elements(By.CLASS_NAME, 'loader-progress-bar-component'):
        time.sleep(1)
    print('Message page loaded. Commencing messaging.')

    # Iterate through the names provided
    blocked_users = []
    n = 1
    for name in list_of_names:
        fill_recipient(name)
        send_message(name, delay=12)
        new_message()
        n += 1

    # Display list of blocked users
    print('Program finished.')
    if blocked_users:
        print('All users messaged except for the following:')
        for user in blocked_users:
            print(user)
    else:
        print('All users messaged.')
