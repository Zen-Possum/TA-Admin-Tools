# ======================================================================================================================
# MatchMonitor.py searches a club match for timeouts and early resignations (before move 10) and returns a list of users
# to which these belong. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client, get_club_matches, get_team_match, get_team_match_board
import chess
import chess.engine
import pandas as pd

# from HermesBot import *

if __name__ == '__main__':
    client.Client.request_config["headers"]["User-Agent"] = (
        "TeamAustraliaAdminScripts"
        "Contact me at aidan.cash93@gmail.com"
    )
    engine_path = 'C:/Users/aidan/Downloads/stockfish/stockfish-windows-x86-64-avx2.exe'
    club = 'team-australia'
    delay = 0
    matches_since = 1726315383
    csv_name = 'match-monitor.csv'
    archive_1 = True

    # Function to determine whether a specified colour is lost from a FEN
    def is_losing(colour, fen):
        board = chess.Board(fen)
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            result = engine.analyse(board, chess.engine.Limit(time=3.0))
            evaluation = result['score'].white().score(mate_score=10000)
            return (evaluation <= -250 and colour == 'white') or (evaluation >= 250 and colour == 'black')

    # Function to write the message to be sent
    def message(match_opponent, offences=0):
        if offences == 0:
            return 'Dear Team Australia member\n\n' \
                   f'We note that you have recently timed out in your game(s) in our match against {match_opponent}. ' \
                   'We understand that keeping up to date with games can be difficult, but it does affect our team\'s' \
                   ' performance in the leagues we compete in. Since this is the first time, this is just a friendly ' \
                   'warning that this violates our timeout policy linked below.\n\n' \
                   'Any future breaches will incur a strike, two of which will mean your team membership will likely ' \
                   'be cancelled, so please have a read of the timeout policy.\n\n' \
                   'Thank you,\n' \
                   'ZenPossum (admin)\n\n' \
                   'Timeout policy can be found at https://www.chess.com/clubs/forum/view/team-australia-timeout-policy'
        elif offences == 1:
            return 'Dear Team Australia member\n\n' \
                   f'We note that you have recently timed out in your game(s) in our match against {match_opponent}. ' \
                   'We understand that keeping up to date with games can be difficult, but it does affect our team\'s' \
                   ' performance in the leagues we compete in. Since this is not the first time, a strike has been ' \
                   'recorded against your name for violating our timeout policy linked below.\n\n' \
                   'Any future breaches will incur a second strike, which will mean your team membership will likely ' \
                   'be cancelled, so please have a read of the timeout policy.\n\n' \
                   'Thank you,\n' \
                   'ZenPossum (admin)\n\n' \
                   'Timeout policy can be found at https://www.chess.com/clubs/forum/view/team-australia-timeout-policy'
        elif offences == 2:
            return 'Dear Team Australia member\n\n' \
                   f'We note that you have recently timed out in your game(s) in our match against {match_opponent}. ' \
                   'We understand that keeping up to date with games can be difficult, but it does affect our team\'s' \
                   ' performance in the leagues we compete in. Since this is not the first time, a strike has been ' \
                   'recorded against your name for violating our timeout policy linked below.\n\n' \
                   'Unfortunately, this is your second strike, which will mean your team membership will be reviewed ' \
                   'by an admin and likely cancelled.\n\n' \
                   'Thank you,\n' \
                   'ZenPossum (admin)\n\n' \
                   'Timeout policy can be found at https://www.chess.com/clubs/forum/view/team-australia-timeout-policy'
        else:
            raise ValueError


    # Download the matches before `matches_since`
    all_matches = get_club_matches(club, tts=delay).json['matches']['in_progress']
    match_ids = [m['@id'].split('/')[-1] for m in all_matches if m['start_time'] >= matches_since
                 and m['time_class'] == 'daily'
                 and m['name'].startswith(('WL', 'AL', '1WL'))]
    print(f'{len(match_ids)} matches found')

    try:
        # Open previous CSV if it exists
        df = pd.read_csv(csv_name)
        print('Previous database loaded from file')
        if archive_1:
            df.to_csv('match-monitor-archive.csv', index=False)
    except FileNotFoundError:
        # Create a dataframe to store the timeouts and early resignations
        df = pd.DataFrame(columns=['username',
                                   'match',
                                   'match_opponent',
                                   'board',
                                   'colour',
                                   'result',
                                   'opponent',
                                   'number_of_moves',
                                   # 'link',
                                   'contacted'])
        print('New database created')

    M = len(match_ids)
    m = 1  # Counter for match number
    for match_id in match_ids:
        # Get the match data from the API
        match_details = get_team_match(match_id, tts=delay).json['match']
        teams = match_details['teams']

        # Skip finished matches (relevant for custom match list only)
        # if match_details['status'] == 'finished':
        #     continue

        # Get the team number based on the club name provided
        team = [t for t in teams.keys() if teams[t]['url'].split('/')[-1] == club][0]
        other_team = [t for t in teams.keys() if not teams[t]['url'].split('/')[-1] == club][0]
        match_opponent = teams[other_team]['name']
        match = teams[team]['players']
        N = len(match)

        # Iterate through the players in the match
        print(f'Beginning match {match_id} ({m} of {M}). Inspecting {N} members for violations.')
        n = 1  # Counter for player number
        for player in match:
            username = player['username']
            board = player['board'].split('/')[-1]
            for colour in ['white', 'black']:
                # Check if (username, match, colour) pair already appears in `df`
                if not ((df['username'] == username) &
                        (df['match'] == int(match_id)) &
                        (df['colour'] == colour)).any():
                    try:
                        result = player[f'played_as_{colour}']
                        if result == 'timeout' or result == 'resigned':
                            # Get more details about the game
                            board_details = get_team_match_board(match_id, board, tts=delay).json['match_board']
                            opponent = [u for u in board_details['board_scores'].keys() if u != username][0]
                            for g in board_details['games']:
                                url_given = isinstance(g[colour], str)
                                # Sometimes the white player is given as an API URL instead of a dictionary
                                if url_given:
                                    if g[colour].split('/')[-1] == username:
                                        game = g
                                elif g[colour]['username'].lower() == username:
                                    game = g
                            number_of_moves = int(game['fen'].split()[-1])
                            # link = game['url']

                            resigned_early = (result == 'resigned') and (number_of_moves < 10) and is_losing(colour, game['fen'])
                            if result == 'timeout' or resigned_early:
                                # Add a row to the data frame
                                df_to_add = pd.DataFrame({
                                    'username': [username],
                                    'match': [match_id],
                                    'match_opponent': [match_opponent],
                                    'board': [board],
                                    'colour': [colour],
                                    'result': [result],
                                    'opponent': [opponent],
                                    'number_of_moves': [number_of_moves],
                                    # 'link': [link],
                                    'contacted': [None]
                                })
                                df = pd.concat([df, df_to_add], ignore_index=True)
                    except KeyError:
                        # This is if the games are still ongoing
                        pass
            n += 1
        m += 1

    # Sort and save the collected data
    # df = df.sort_values(['match', 'board'], ascending=True)
    df.to_csv(csv_name, index=False)
    print(f'Program finished. Data saved as {csv_name}.')

# TODO: check for strikes and keep count
# TDOO: alert if need to ban someone
# TODO: integrate with google sheets to update rather than just list
# TODO: integrate with HermesBot.py
