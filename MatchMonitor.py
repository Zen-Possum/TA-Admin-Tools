# ======================================================================================================================
# MatchMonitor.py searches a club match for timeouts and early resignations (before move 10) and returns a list of users
# to which these belong. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client
import pandas as pd
from datetime import date

if __name__ == '__main__':
    club = 'team-australia'
    delay = 0
    match_id = 1500903  # Find this at the end of the match URL

    # Get the match data from the API
    teams = client.get_team_match(match_id, tts=delay).json['match']['teams']

    # Get the team number based on the club name provided
    team = [t for t in teams.keys() if teams[t]['url'].split('/')[-1] == club][0]
    match = teams[team]['players']
    N = len(match)

    # Create a dataframe to store the undesirable results
    df = pd.DataFrame(columns=['username', 'board', 'colour', 'result', 'number_of_moves', 'link'])

    # Iterate through the players in the match
    print(f'Program started . Inspecting {N} members for violations.')
    n = 1
    for player in match:
        username = player['username']
        board = player['board'].split('/')[-1]
        for colour in ['white', 'black']:
            try:
                result = player[f'played_as_{colour}']
                if result == 'timeout' or result == 'resigned':
                    # Get more details about the game
                    board_games = client.get_team_match_board(match_id, board, tts=delay).json['match_board']['games']
                    for g in board_games:
                        url_given = isinstance(g[colour], str)
                        # Sometimes the white player is given as an API URL instead of a dictionary
                        if url_given:
                            if g[colour].split('/')[-1] == username:
                                game = g
                        elif g[colour]['username'].lower() == username:
                            game = g
                    number_of_moves = int(game['fen'].split()[-1]) # noqa
                    link = game['url']
                    resigned_early = (result == 'resigned') and (number_of_moves < 10)
                    if result == 'timeout' or resigned_early:
                        # Add a row to the data frame
                        df_to_add = pd.DataFrame({
                            'username': [username],
                            'board': [board],
                            'colour': [colour],
                            'result': [result],
                            'number_of_moves': [number_of_moves],
                            'link': [link]
                        })
                        df = pd.concat([df, df_to_add], ignore_index=True)
            except KeyError:
                # This is if the games are still ongoing
                pass
        n += 1

    # Sort and save the collected data
    df = df.sort_values('board', ascending=True)
    csv_name = f'match-{match_id}-{date.today()}.csv'
    df.to_csv(csv_name, index=False)
    print(f'Program finished. Data saved as {csv_name}.')
