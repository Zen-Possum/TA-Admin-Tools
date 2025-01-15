# ======================================================================================================================
# MultipleStateMemberships.py identifies Team Australia members in other World League (WL) clubs.
# Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client
import pandas as pd
from datetime import date
from FilterFunctions import get_all_members
from selenium import webdriver
from Credentials import username, password
import time

# Parameters
home_club = 'team-australia'
url_to_scrape = 'https://www.chess.com/clubs/forum/view/wl2023-teams-and-representatives'
login_url = f'https://www.chess.com/login_and_go?returnUrl={url_to_scrape}'
delay = 0

# Set up user agent
client.Client.request_config['headers']['User-Agent'] = (
    'TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)

# Log in to WCL page
driver = webdriver.Chrome(executable_path=driver_path)
driver.get(login_url)
login_boxes = driver.find_elements_by_class_name('login-input')
login_boxes[0].send_keys(username)
login_boxes[1].send_keys(password)
driver.find_element_by_id('login').click()
time.sleep(3)

# Scrape a list of WL clubs
link_elements = driver.find_elements_by_xpath('//div/p/a') + \
                driver.find_elements_by_xpath('//div/p/span/a') + \
                driver.find_elements_by_xpath('//div/p/span/span/a') + \
                driver.find_elements_by_xpath('//div/p/span/span/span/a')
links = [link.get_attribute('href') for link in link_elements]
international_clubs = set([link.split('/')[-1] for link in links if link.startswith('https://www.chess.com/club/')])
international_clubs.remove(home_club)

# Get lists of members for all clubs of interest
au_members = set(get_all_members(home_club))  # Members of home club
international_members = set()  # Members of all other WL clubs combined
members_of = {}  # Dictionary with members of each club
for club in international_clubs:
    club_details = client.get_club_details(club, tts=delay).json['club']
    members_of[club] = get_all_members(club)
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
csv_name = f'multiple-national-memberships-{date.today()}.csv'
df.to_csv(csv_name, index=False)
