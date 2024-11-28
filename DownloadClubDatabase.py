# ======================================================================================================================
# DownloadClubDatabase.py downloads data from all the members of a chess.com club into a single CSV file using
# the chess.com API. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client, get_player_stats, get_player_profile
import pandas as pd
import time
from datetime import date
from FilterMembers import get_all_members

# TODO: make more efficient so it only gets each player once
# TODO: make a script that checks if players are in two state clubs

if __name__ == '__main__':
    # Parameters
    all_clubs = [
        # 'team-australia-adelaide-sa',
        # 'team-australia-brisbane-qld',
        # 'team-australia-canberra-act',
        # 'team-australia-darwin-nt',
        # 'team-australia-hobart-tasmania',
        # 'team-australia-melbourne-vic',
        # 'team-australia-perth-w-a',
        # 'team-australia-sydney-nsw',
        'team-australia'
    ]
    C = len(all_clubs)
    delay = 0

    c = 1
    # Iterate through clubs
    for club in all_clubs:
        # Get a list of all club members
        club_members = get_all_members(club)
        N = len(club_members)

        # Initialise dataframe and loop timing variables
        df = pd.DataFrame(columns=['username', 'country', 'days_since_online', 'name', 'location',
                                   'timeout_percent', 'chess_daily', 'chess960_daily',
                                   'chess_rapid', 'chess_blitz', 'chess_bullet'])
        print(f'Program started for club "{club}" ({c} of {C}). Downloading {N} members into database.')
        n = 1
        last_time = time.time()

        # Iterate through club members
        for member in club_members:
            # Display progress and estimated time remaining in loop
            if n % 100 == 0:
                current_time = time.time()
                estimated_time_remaining = (N - n) * (current_time - last_time) / 50 / 60  # in minutes
                last_time = current_time
                print(f'Processing member {n} of {N}. Estimated time remaining: '
                      f'{pd.Timedelta(estimated_time_remaining, "min").round(freq="s")}.')

            # Query the API for the player's data
            profile = get_player_profile(member, tts=delay).json['player']
            stats = get_player_stats(member, tts=delay).json['stats']

            # Extract all data of interest from the player's profile
            df_to_add = pd.DataFrame({'username': [member],
                                      'country': [profile['country'].split('/')[-1]],
                                      'days_since_online': [
                                          round((time.time() - profile['last_online']) / (60 * 60 * 24), 1)]
                                      })
            # Extract player's name and location if they exist
            for field in ['name', 'location']:
                try:
                    df_to_add[field] = profile[field]
                except KeyError:
                    df_to_add[field] = None

            # Extract player's timeout percent if it exists
            try:
                df_to_add['timeout_percent'] = stats['chess_daily']['record']['timeout_percent']
            except KeyError:
                df_to_add['timeout_percent'] = None

            # Extract player's ratings if they exist
            for format in ['chess_daily', 'chess960_daily', 'chess_rapid', 'chess_blitz', 'chess_bullet']:
                try:
                    df_to_add[format] = stats[format]['last']['rating']
                except KeyError:
                    df_to_add[format] = None

            # Join player's data to the main dataframe
            df = pd.concat([df, df_to_add], ignore_index=True)
            n += 1

        df = df.sort_values('chess_daily', ascending=False)
        csv_name = f'{club}-{date.today()}.csv'
        df.to_csv(csv_name, index=False)
        print(f'Program finished for club "{club}" ({c} of {C}). Database saved as {csv_name}.')
        c += 1
