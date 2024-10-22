from chessdotcom import client
from FilterMembers import get_all_members

client.Client.request_config["headers"]["User-Agent"] = (
    "TeamAustraliaAdminScripts"
    "Contact me at aidan.cash93@gmail.com"
)
country_code = 'AU'
club = 'team-australia'
delay = 0

country_players = client.get_country_players(country_code).json['players']  # Change to manually scraping leaderboard
club_players = get_all_members(club)

# Compute set minus
print(len(country_players))
recruitees = list(set(country_players)-set(club_players))
print(len(recruitees))
# Message distribution


# Message execution