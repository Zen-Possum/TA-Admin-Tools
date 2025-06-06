# ======================================================================================================================
# MultipleStateMemberships.py identifies players in multiple Team Australia state/territory clubs, ignoring admins.
# Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client, get_club_details, errors
from collections import Counter
import pandas as pd
from datetime import date
from FilterFunctions import get_all_members

# Parameters
all_clubs = [
        'team-australia-adelaide-sa',
        'team-australia-brisbane-qld',
        'team-australia-canberra-act',
        'team-australia-darwin-nt',
        'team-australia-hobart-tasmania',
        'team-australia-melbourne-vic',
        'team-australia-perth-w-a',
        'team-australia-sydney-nsw'
    ]
delay = 0
csv_name = f'Data/multiple-state-memberships-{date.today()}.csv'

# Set up user agent
client.Client.request_config['headers']['User-Agent'] = (
    'TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)

all_members = []  # Members of all clubs combined
members_of = {}  # Dictionary with members of each club
print('Member lists:')
for club in all_clubs:
    club_details = get_club_details(club, tts=delay).json['club']
    club_admins = [api_url.split('/')[-1] for api_url in club_details['admin']]
    try:
        club_members = get_all_members(club)
        print(f'{club}: public')
    except errors.ChessDotComClientError:
        # If club members are private
        club_members = []
        print(f'{club}: private')
    members_of[club] = [m for m in club_members if m not in club_admins]
    all_members += members_of[club]

# Check for duplicates and tabulate them
counter = Counter(all_members)
duplicates = [element for element, count in counter.items() if count > 1]
df = pd.DataFrame(columns=['username', 'clubs', 'link', 'contacted'])
for member in duplicates:
    multiple_clubs = [club[15:] for club in all_clubs if member in members_of[club]]
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
