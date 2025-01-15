# ======================================================================================================================
# RecruitTopAustralians.py messages the highest-rated Australians not currently in Team Australia.
# Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client, get_country_players
from FilterFunctions import get_all_members

# Parameters
country_code = 'AU'
club = 'team-australia'
delay = 0

# Set up user agent
client.Client.request_config['headers']['User-Agent'] = (
    'TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)

# Get a list of players in a country and in the club
country_players = get_country_players(country_code).json['players']
club_players = get_all_members(club)

# Compute set minus
print(len(country_players))
players_to_recruit = list(set(country_players)-set(club_players))
print(len(players_to_recruit))

# Message distribution

# Message execution

# TODO: work in progress
# TODO: currently there is a hard limit of 10 000 players, will need to change to manually scraping leaderboard
