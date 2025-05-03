# ======================================================================================================================
# MultipleStateMemberships.py identifies Team Australia members in other World League (WL) clubs.
# Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client, errors
import pandas as pd
from datetime import date
from FilterFunctions import get_all_members
from Credentials import username, password
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Parameters
home_club = 'team-australia'
url_to_scrape = 'https://www.chess.com/clubs/forum/view/wl2025-list-of-teams'
login_url = f'https://www.chess.com/login_and_go?returnUrl={url_to_scrape}'
delay = 0
csv_name = f'Data/multiple-national-memberships-{date.today()}.csv'

# Initiate driver and user agent
client.Client.request_config['headers']['User-Agent'] = (
    'TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)
options = Options()
options.add_argument(
    'user-agent=TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(login_url)

# Login using credentials
login_boxes = driver.find_elements(By.CLASS_NAME, 'cc-input-component')
login_boxes[1].send_keys(username)
login_boxes[2].send_keys(password)
driver.find_element(By.ID, 'login').click()
time.sleep(2)

# Scrape a list of WL clubs
link_elements = driver.find_elements(By.XPATH, '//div/p/a')
link_elements.pop()
links = [link.get_attribute('href') for link in link_elements]
international_clubs = set([link.split('/')[-1] for link in links if link.startswith('https://www.chess.com/club/')])
international_clubs.remove(home_club)
driver.close()

# Get lists of members for all clubs of interest
au_members = set(get_all_members(home_club))  # Members of home club
international_members = set()  # Members of all other WL clubs combined
members_of = {}  # Dictionary with members of each club
for club in international_clubs:
    try:
        # Get club members
        members_of[club] = get_all_members(club)
    except errors.ChessDotComClientError:
        # If club member list is private
        members_of[club] = []
    international_members.update(members_of[club])

# Check for overlaps and tabulate them
duplicates = au_members.intersection(international_members)
df = pd.DataFrame(columns=['username', 'clubs', 'link', 'contacted'])
for member in duplicates:
    multiple_clubs = [club for club in international_clubs if member in members_of[club]]
    df_to_add = pd.DataFrame({
        'username': [member],
        'clubs': [', '.join(multiple_clubs)],
        'link': [f'https://www.chess.com/member/{member}'],
        'contacted': [None]
    })
    df = pd.concat([df, df_to_add], ignore_index=True)

# Save to CSV file
df = df.sort_values('username')
df.to_csv(csv_name, index=False)
