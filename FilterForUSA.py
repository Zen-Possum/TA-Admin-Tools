# ======================================================================================================================
# FilterForUSA.py filters Team Australia members to those matching the following criteria:
#   * Over a specified rating,
#   * Below 25% timeout percentage,
#   * Last online in the last 3 days, and
#   * Not already in a specified team match.
# It then writes the results to a Google Sheets document and divides the players into N folds. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client
import pandas as pd
import time
from FilterMembers import get_all_members

if __name__ == '__main__':
    # Parameters
    club = 'team-australia'
    team = 'team1'  # TODO: automatically detect from team @id
    format = 'chess_daily'
    # TODO: automatically detect from get_team_match(match_id, tts=delay).json['match']['settings']
    delay = 0
    match_id = 1500903  # Find this at the end of the match URL
    min_rating = 1200
    max_timeout_percent = 25
    max_days_since_online = 3  # TODO: reported as a bit buggy

    # club_members = get_all_members(club)
    club_members = ['']
    match_raw = client.get_team_match(match_id, tts=delay).json['match']['teams'][team]['players']
    # print(client.get_team_match(match_id, tts=delay).json['match'])
    match = [x['username'] for x in match_raw]
    filtered_members = pd.DataFrame(columns=['username', 'rating', 'timeout_percent', 'days_since_online'])

    # Iterate through club members
    for member in club_members:
        if member not in match:
            stats = client.get_player_stats(member, tts=delay).json['stats'][format]
            rating = stats['last']['rating']
            print(rating)
            timeout_percent = stats['record']['timeout_percent']
            print(timeout_percent)
            if rating > min_rating and timeout_percent < max_timeout_percent:
                last_online = client.get_player_profile(member, tts=delay).json['player']['last_online']
                print(last_online)
                days_since_online = (time.time() - last_online) / (60 * 60 * 24)
                print(days_since_online)
                if days_since_online < max_days_since_online:
                    df_to_add = pd.DataFrame({'username': [member],
                                              'rating': [rating],
                                              'timeout_percent': [timeout_percent],
                                              'days_since_online': [days_since_online]})
                    print(df_to_add)
                    filtered_members = pd.concat([filtered_members, df_to_add], ignore_index=True)

    print(filtered_members)
