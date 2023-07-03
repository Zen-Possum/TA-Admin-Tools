# ======================================================================================================================
# HermesBot.py automates sending the same message to multiple users on chess.com, which can be specified in list or CSV
# format. It requires an up-to-date chrome driver (https://chromedriver.chromium.org/downloads) and valid chess.com
# login credentials. Written by ZenPossum :)
# ======================================================================================================================

from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# 1. Input your login credentials here
username = 'USERNAME_HERE'
password = 'PASSWORD_HERE'

# 2. Input the list of users to send the message to here, either using a CSV with a 'username' column or manually
file_name = 'FILE_NAME_HERE.csv'  # Leave blank with `file_name = None` to use the manual list
if file_name:
    df = pd.read_csv(file_name)
    list_of_names = list(df['username'])
else:
    list_of_names = ['ZenPossum']
N = len(list_of_names)

# 3. Input the message you want to send here
message = 'MESSAGE_HERE. USE \n FOR NEW LINES.'

# 4. Input your chrome driver path here
driver_path = r'C:\PATH\TO\chromedriver.exe'
driver = webdriver.Chrome()  # May need to specify executable_path=driver_path)
driver.get('https://www.chess.com/messages/compose')


def login(driver, username, password):
    # LOGIN logs in using the given credentials
    login_boxes = driver.find_elements_by_class_name('login-input')
    login_boxes[0].send_keys(username)
    login_boxes[1].send_keys(password)
    driver.find_element_by_id('login').click()
    return driver


def write_plain_text(text, driver):
    # WRITE_PLAIN_TEXT writes plain text to the message box
    driver.find_element_by_id('tinymce').send_keys(text)
    return driver


def write_bold_text(text, driver):
    # WRITE_PLAIN_TEXT writes bold text to the message box
    driver.find_element_by_id('tinymce').send_keys(Keys.CONTROL + 'b')
    driver.find_element_by_id('tinymce').send_keys(text)
    driver.find_element_by_id('tinymce').send_keys(Keys.CONTROL + 'b')
    return driver


def write_italics_text(text, driver):
    # WRITE_PLAIN_TEXT writes italics text to the message box
    driver.find_element_by_id('tinymce').send_keys(Keys.CONTROL + 'i')
    driver.find_element_by_id('tinymce').send_keys(text)
    driver.find_element_by_id('tinymce').send_keys(Keys.CONTROL + 'i')
    return driver


def send_message(driver, name, delay=12):
    # SEND_MESSAGE sends a message to a single user
    address_box = driver.find_elements_by_class_name('form-input-left')
    address_box[1].send_keys(name)
    time.sleep(1)
    driver.find_element_by_class_name('username-search-autocomplete-field').click()
    time.sleep(1)
    try:
        driver.switch_to.frame('mce_0_ifr')  # Switch frames for rich text editor
        # MESSAGE SEQUENCE HERE
        driver.switch_to.default_content()  # Switch back
        driver.find_element_by_id('message-submit').click()  # Send message
        print(f'Sent message to {name} ({n} of {N})')
        time.sleep(delay)
    except common.exceptions.ElementNotInteractableException:  # If user cannot be messaged
        print(f'Unable to message {name} ({n} of {N}).')
        blocked_users.append(name)
        address_box[1].clear()
    except common.exceptions.NoSuchElementException:  # Alternate version of above
        print(f'Unable to message {name} ({n} of {N}).')
        blocked_users.append(name)
        address_box[1].clear()
    return driver


def new_message(driver):
    # NEW_MESSAGE prepares the page to compose a new message
    driver.find_element_by_class_name('message-list-search-compose').click()
    time.sleep(1)
    return driver


if __name__ == '__main__':
    # Log in to the messaging portal
    login(driver, username, password)
    print('Logged in.')

    # Wait for page to load before sending messages
    print('Loading message page...')
    while driver.find_elements_by_class_name('loader-progress-bar-component'):
        time.sleep(1)
    print('Message page loaded. Commencing messaging.')

    # Iterate through the names provided
    blocked_users = []
    n = 1
    for name in list_of_names:
        send_message(driver, name, delay=12)
        new_message(driver)
        n += 1

    # Display list of blocked users
    print('Program finished.')
    if blocked_users:
        print('All users messaged except for the following:')
        for user in blocked_users:
            print(user)
    else:
        print('All users messaged.')
