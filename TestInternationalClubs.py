from chessdotcom import client
from FilterMembers import get_all_members, pretty_print
from datetime import date

home_club = 'team-australia'
delay = 0

url_to_scrape = 'https://www.chess.com/clubs/forum/view/wl2023-teams-and-representatives'
international_clubs = []
# Sign in and scrape URL data for club list
# ...
# Remove team-australia

all_members = get_all_members(home_club)
n = 1
for member in all_members:
    player_clubs_raw = client.get_player_clubs(member, tts=delay).json['clubs']
    player_clubs = [c['url'].split('/')[-1] for c in player_clubs_raw]
    if [c for c in player_clubs if c in international_clubs]:
        pass
    # pretty_print(player_clubs)
    print(n)
    n += 1
