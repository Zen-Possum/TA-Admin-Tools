# ======================================================================================================================
# MultipleStateMemberships.py identifies Team Australia members in other World League clubs.
# Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client
import pandas as pd
from datetime import date
from FilterMembers import get_all_members

home_club = 'team-australia'
delay = 0

url_to_scrape = 'https://www.chess.com/clubs/forum/view/wl2023-teams-and-representatives'
international_clubs = []
# Sign in and scrape URL data for club list
# ...
# Remove team-australia

au_members = set(get_all_members(home_club))
n = 1

########################################################################################################################
#
# for member in au_members:
#     player_clubs_raw = client.get_player_clubs(member, tts=delay).json['clubs']
#     player_clubs = [c['url'].split('/')[-1] for c in player_clubs_raw]
#     if [c for c in player_clubs if c in international_clubs]:
#         pass
#     # pretty_print(player_clubs)
#     print(n)
#     n += 1
#
########################################################################################################################

international_members = set()  # Members of all clubs combined
members_of = {}  # Dictionary with members of each club
for club in international_clubs:
    club_details = client.get_club_details(club, tts=delay).json['club']
    members_of[club] = get_all_members(club)
    international_members.update(members_of[club])

# Check for duplicates and tabulate them
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
