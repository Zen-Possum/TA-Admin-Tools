# ======================================================================================================================
# FilterForUSA.py filters Team Australia members to those matching the following criteria:
#   * Over a specified rating,
#   * Below 25% timeout percentage,
#   * Last online in the last few days, and
#   * Not already in a specified team match.
# It then writes the results to a Google Sheets document and divides the players into folds. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client
import pandas as pd
import time
from FilterMembers import get_all_members
import json
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

if __name__ == '__main__':
    # Parameters
    club = 'team-australia'
    file_name = 'FilteredMembersBulgaria.csv'
    delay = 0.2
    match_id = 1529009  # Find this at the end of the match URL
    min_rating = 1200
    max_rating = 4000
    max_timeout_percent = 25
    max_days_since_online = 7

    # Get the list of club members
    # club_members = get_all_members(club)
    ###
    with open('members.json') as json_file:
        all_members_raw = json.load(json_file)
    club_members = []
    for category in ['weekly', 'monthly', 'all_time']:
        club_members += [x['username'] for x in all_members_raw[category]]
    ###
    N = len(club_members)

    # Get the match data from the API
    match_raw = client.get_team_match(match_id, tts=delay).json['match']
    teams = match_raw['teams']
    settings = match_raw['settings']

    # Get the team number and format based on the club name and match ID provided
    team = [t for t in teams.keys() if teams[t]['url'].split('/')[-1] == club][0]
    format = f'{settings["rules"]}_{settings["time_class"]}'
    match = [x['username'] for x in teams[team]['players']]
    filtered_members = pd.DataFrame(columns=['username', 'rating', 'timeout_percent', 'days_since_online'])

    # Iterate through club members
    n = 1
    last_time = time.time()
    for member in club_members:
        if n % 50 == 0:
            current_time = time.time()
            estimated_time_remaining = round((N - n) * (current_time - last_time) / 50 / 60)
            last_time = current_time
            print(f'Processing member {n} of {N}. Estimated time remaining: {estimated_time_remaining} minutes.')
        if member not in match:
            try:
                stats = client.get_player_stats(member, tts=delay).json['stats'][format]
                rating = stats['last']['rating']
                timeout_percent = stats['record']['timeout_percent']
            except KeyError:
                n += 1
                continue
            if min_rating <= rating <= max_rating and timeout_percent < max_timeout_percent:
                last_online = client.get_player_profile(member, tts=delay).json['player']['last_online']
                days_since_online = (time.time() - last_online) / (60 * 60 * 24)
                if days_since_online < max_days_since_online:
                    df_to_add = pd.DataFrame({'username': [member],
                                              'rating': [rating],
                                              'timeout_percent': [timeout_percent],
                                              'days_since_online': [round(days_since_online, 1)]})
                    filtered_members = pd.concat([filtered_members, df_to_add], ignore_index=True)
        n += 1
    filtered_members = filtered_members.sort_values('rating', ascending=False)
    filtered_members.to_csv(file_name, index=False)
