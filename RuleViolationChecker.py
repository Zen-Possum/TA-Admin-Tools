# ======================================================================================================================
# RuleViolationChecker.py checks the club members' profiles for violation of the club rules, namely flying a different
# country's flag or having profanities in their profile. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client, get_player_profile
import pandas as pd
from datetime import date
from FilterFunctions import get_all_members
import time
import profanity_check

# Parameters
home_club = 'team-australia'
delay = 0
file_name = f'Data/rule-violations-{date.today()}.csv'
database_file_name = f'Data/team-australia-{date.today()}.csv'
use_database = True  # Download a database of club members using DownloadClubDatabase.py first for speed

# Set up user agent
client.Client.request_config['headers']['User-Agent'] = (
    'TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)

# Get a list of club members
club_members = get_all_members(home_club)
filtered_members = pd.DataFrame(columns=['username', 'reason', 'country', 'profanity', 'link'])
N = len(club_members)
n = 1
last_time = time.time()

if use_database:
    # Iterate through club members in existing database
    df = pd.read_csv(database_file_name)
    for index, row in df.iterrows():
        member = row['username']
        country_code = row['country']

        # Check for non-AU flag
        if country_code != 'AU':
            df_to_add = pd.DataFrame({'username': [member],
                                      'reason': ['flag'],
                                      'country': [country_code],
                                      'profanity': [''],
                                      'link': [f'https://www.chess.com/member/{member}']})
            filtered_members = pd.concat([filtered_members, df_to_add], ignore_index=True)

        # Check for profanity
        for field in ['username', 'name', 'location']:
            if pd.notna(row[field]) and profanity_check.predict([row[field]]):
                df_to_add = pd.DataFrame({'username': [member],
                                          'reason': [f'profanity in {field}'],
                                          'country': [''],
                                          'profanity': [row[field]],
                                          'link': [f'https://www.chess.com/member/{member}']})
                filtered_members = pd.concat([filtered_members, df_to_add], ignore_index=True)
                break

else:
    # Iterate through club members using the API
    for member in club_members:
        if n % 50 == 0:
            # Display progress and estimated time remaining in loop
            current_time = time.time()
            estimated_time_remaining = round((N - n) * (current_time - last_time) / 50 / 60)
            last_time = current_time
            print(f'Processing member {n} of {N}. Estimated time remaining: '
                  f'{pd.Timedelta(estimated_time_remaining, "min").round(freq="s")}.')

        # Check for non-AU flag
        profile = get_player_profile(member, tts=delay)
        country_code = profile.json['player']['country'].split('/')[-1]
        if country_code != 'AU':
            df_to_add = pd.DataFrame({'username': [member],
                                      'reason': ['flag'],
                                      'country': [country_code],
                                      'profanity': [''],
                                      'link': [f'https://www.chess.com/member/{member}']})
            filtered_members = pd.concat([filtered_members, df_to_add], ignore_index=True)

        # Check for profanity
        profile_fields = profile.json['player']
        for field in ['username', 'name', 'location']:
            try:
                if profanity_check.predict([profile_fields[field]]):
                    df_to_add = pd.DataFrame({'username': [member],
                                              'reason': [f'profanity in {field}'],
                                              'country': [''],
                                              'profanity': [profile_fields[field]],
                                              'link': [f'https://www.chess.com/member/{member}']})
                    filtered_members = pd.concat([filtered_members, df_to_add], ignore_index=True)
                    break
            except KeyError:
                continue
        n += 1

# Sort and save as a CSV file
filtered_members = filtered_members.sort_values('reason')
filtered_members.to_csv(file_name, index=False)
