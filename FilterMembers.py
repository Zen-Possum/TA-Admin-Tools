# ======================================================================================================================
# FilterMembers.py provides a set of useful functions for filtering or identifying chess.com club members which meet
# certain criteria including rating, flag, obscene profiles or timeout percentages. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client
import pandas as pd
import profanity_check

# Set the club URL suffix and the rate limit delay here
club_name = 'team-australia'
delay = 1
recoded = {'Bullet': 'chess_bullet', 'Blitz': 'chess_blitz', 'Rapid': 'chess_rapid',
           'Daily': 'chess_daily', 'Daily960': 'chess960_daily'}


def get_all_members(club):
    all_members_raw = client.get_club_members(club, tts=delay)
    all_members = []
    for category in ['weekly', 'monthly', 'all_time']:
        all_members += [x['username'] for x in all_members_raw.json['members'][category]]
    return all_members


def filter_by_rating(members, format, bottom, top, to_csv=False):
    # FILTER_BY_RATING filters a list of members to only include a specified rating range in the given format and
    # returns a dictionary of their usernames and ratings.
    # Formats available: 'Bullet', 'Blitz', 'Rapid', 'Daily', 'Daily960'
    filtered_members = {}
    for member in members:
        stats = client.get_player_stats(member, tts=delay)
        rating = stats.json['stats'][recoded[format]]['last']['rating']
        if bottom <= rating <= top:
            filtered_members[member] = rating
    if to_csv:
        pd.DataFrame(filtered_members.items(), columns=['name', format]).to_csv('filtered_ratings.csv', index=False)
    return filtered_members


def find_non_au_flags(members, to_csv=False):
    # FIND_NON_AU_FLAGS filters a list of members and returns a dictionary including members with non-Australian flags
    # and their current flags. There is also an option to save the results as a CSV file.
    filtered_members = {}
    for member in members:
        profile = client.get_player_profile(member, tts=delay)
        country_code = profile.json['player']['country'].split('/')[-1]
        if country_code != 'AU':
            filtered_members[member] = country_code
    if to_csv:
        pd.DataFrame(filtered_members.items(), columns=['name', 'country']).to_csv('non-au-flags.csv', index=False)
    return filtered_members


def find_profanity(members, to_csv=False):
    # FIND_PROFANITY filters a list of members and returns a dictionary containing members with profanities in their
    # username, name or location and the offending text. Currently searching the profile description is unavailable.
    filtered_members = {}
    for member in members:
        profile = client.get_player_profile(member, tts=delay)
        profile_fields = profile.json['player']
        for field in ['name', 'username', 'location']:
            if profanity_check.predict(profile_fields[field]):
                filtered_members[member] = profile_fields[field]
                break
    if to_csv:
        pd.DataFrame(filtered_members.items(), columns=['name', 'text']).to_csv('profanities.csv', index=False)
    return filtered_members


def filter_timeout_percentage(members, format, above=25, to_csv=False):
    # FILTER_TIMEOUT_PERCENTAGE takes a list of members and returns a dictionary of members with timeout percentages
    # larger than the `above` parameter in the specified format ('Daily' or 'Daily960').
    filtered_members = {}
    for member in members:
        stats = client.get_player_stats(member, tts=delay)
        percentage = stats.json['stats'][recoded[format]]['record']['timeout_percent']
        if percentage >= above:
            filtered_members[member] = percentage
    if to_csv:
        pd.DataFrame(filtered_members.items(), columns=['name', 'timeout_percentage'])\
            .to_csv('filtered_timeout.csv', index=False)
    return filtered_members
