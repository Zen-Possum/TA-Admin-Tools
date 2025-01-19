# ======================================================================================================================
# VoteCaptain.py formats 'don't vote yet' and 'vote now' messages on a Vote Chess game. It requires an up-to-date chrome
# driver (https://chromedriver.chromium.org/downloads) and valid Chess.com login credentials. Written by ZenPossum :)
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
from HermesBot import set_driver, insert_image, write_plain_text, write_bold_text

options = Options()
options.add_argument(
    'user-agent=TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)


def dont_vote_yet(game_id):
    # DONT_VOTE_YET logs in and posts a 'don't vote yet' image with a footer
    url = f'https://www.chess.com/votechess/game/{game_id}'
    login_url = f'https://www.chess.com/login_and_go?returnUrl={url}'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    set_driver(driver)
    driver.get(login_url)
    time.sleep(1)
    login_boxes = driver.find_elements(By.CLASS_NAME, 'cc-input-component')
    login_boxes[1].send_keys(username)
    login_boxes[2].send_keys(password)
    driver.find_element(By.ID, 'login').click()
    time.sleep(5)
    driver.switch_to.frame('mce_0_ifr')  # Switch frames for rich text editor
    insert_image('https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/ZenPossum/phpbIA36b.png')
    write_plain_text('New to vote chess? Read the guidelines here.\n'
                     'https://www.chess.com/clubs/forum/view/team-australia-vote-chess-guidelines-1 ')
    driver.switch_to.default_content()  # Switch back
    driver.find_element(By.ID, 'message-submit').click()  # Post message


def vote_now(game_id, moves):
    # VOTE_NOW logs in and posts a 'vote now' image with the authorised moves and a footer
    url = f'https://www.chess.com/votechess/game/{game_id}'
    login_url = f'https://www.chess.com/login_and_go?returnUrl={url}'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    set_driver(driver)
    driver.get(login_url)
    time.sleep(1)
    login_boxes = driver.find_elements(By.CLASS_NAME, 'cc-input-component')
    login_boxes[1].send_keys(username)
    login_boxes[2].send_keys(password)
    driver.find_element(By.ID, 'login').click()
    time.sleep(5)
    driver.switch_to.frame('mce_0_ifr')  # Switch frames for rich text editor
    insert_image('https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/ZenPossum/php6Kg5Xp.png')
    write_plain_text('New to vote chess? Read the guidelines here.\n'  # TODO: change to Shift + Enter
                     'https://www.chess.com/clubs/forum/view/team-australia-vote-chess-guidelines-1 ')
    # TODO: Go back to after image
    # TODO: change_font_size(36)
    write_bold_text(moves.pop(0))
    for move in moves:
        write_plain_text(' or ')
        write_bold_text(move)

    driver.switch_to.default_content()  # Switch back
    driver.find_element(By.ID, 'message-submit').click()  # Post message


if __name__ == '__main__':
    deutsch = 311723
    spain = 325815
    turk = 334523
    dont_vote_yet(deutsch)
