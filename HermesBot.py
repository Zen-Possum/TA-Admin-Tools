# ======================================================================================================================
# HermesBot.py automates sending the same message to multiple users on chess.com, which can be specified in list or CSV
# format. It requires an up-to-date chrome driver (https://chromedriver.chromium.org/downloads) and valid chess.com
# login credentials. Written by ZenPossum :)
# ======================================================================================================================

from selenium import webdriver
import time
import pandas as pd

# 1. Input your login credentials here
username = 'USERNAME_HERE'
password = 'PASSWORD_HERE'

# 2. Input the list of users to send the message to here, either using a CSV with a 'name' column or manually
file_name = 'FILE_NAME_HERE.csv'
if file_name:
    df = pd.read_csv(file_name)
    list_of_names = list(df['name'])
else:
    list_of_names = ['ZenPossum']

# 3. Input the message you want to send here
message = 'MESSAGE HERE. USE \n FOR NEW LINES.'

# 4. Input your chrome driver path here
driver_path = r'C:\PATH\TO\chromedriver.exe'
driver = webdriver.Chrome(executable_path=driver_path)
driver.get('https://www.chess.com/messages/compose')


def login(driver, username, password):
    # LOGIN logs in using the given credentials
    login_boxes = driver.find_elements_by_class_name('login-input')
    login_boxes[0].send_keys(username)
    login_boxes[1].send_keys(password)
    driver.find_element_by_id('login').click()
    return driver


def send_message(driver, name, message):
    # SEND_MESSAGE sends a message to a single user
    address_box = driver.find_elements_by_class_name('form-input-left')
    address_box[1].send_keys(name)
    time.sleep(1)
    driver.find_element_by_class_name('username-search-autocomplete-field').click()
    time.sleep(1)
    driver.switch_to.frame('mce_0_ifr')  # Switch frames for rich text editor
    driver.find_element_by_id('tinymce').send_keys(message)
    driver.switch_to.default_content()  # Switch back
    driver.find_element_by_id('message-submit').click()
    time.sleep(1)
    return driver


def new_message(driver):
    # NEW_MESSAGE prepares the page to compose a new message
    driver.find_element_by_class_name('message-list-search-compose').click()
    time.sleep(1)
    return driver


if __name__ == '__main__':
    login(driver, username, password)

    # Wait for page to load before sending messages
    print('Loading message page...')
    while driver.find_elements_by_class_name('loader-progress-bar-component'):
        time.sleep(1)

    # Iterate through the names provided
    for name in list_of_names:
        send_message(driver, name, message)
        print(f'Sent message to {name} ({list_of_names.index(name) + 1} of {len(list_of_names)})')
        new_message(driver)
