# ======================================================================================================================
# MatchMonitor.py searches club matches for timeouts and early resignations (before move 10) and returns a list of users
# to which these belong. Written by ZenPossum :)
# ======================================================================================================================

from chessdotcom import client, get_club_matches, get_team_match, get_team_match_board
import chess
import chess.engine
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from HermesBot import *
from FilterFunctions import get_all_members

# Parameters
engine_path = 'C:/Users/aidan/Downloads/stockfish/stockfish-windows-x86-64-avx2.exe'
club = 'team-australia'
delay = 0
matches_since = 1726315383
csv_name = 'match-monitor.csv'
archive_1 = True  # If you want to save the previous CSV as an archive
ignore_matches_json_name = 'ignore_matches.json'  # Stores matches to ignore (i.e. finished and checked)

# Set up user agent
client.Client.request_config['headers']['User-Agent'] = (
    'TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)


def is_losing(colour, fen):
    # IS_LOSING evaluates a given position and determines if the specified colour is losing by more than 2.5 points
    position = chess.Board(fen)
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        analysis = engine.analyse(position, chess.engine.Limit(time=3.0))
        evaluation = analysis['score'].white().score(mate_score=10000)
        return (evaluation <= -250 and colour == 'white') or (evaluation >= 250 and colour == 'black')


def message_text(username, match_opponent, offences=0):
    # MESSAGE_TEXT returns the text to send in the message based on the number of existing strikes
    if offences == 0:
        return 'Dear Team Australia member\n' \
               'We note that you have recently timed out or resigned early in your game(s) in our match against ' \
               f'{match_opponent}. ' \
               'We understand that keeping up to date with games can be difficult, but it does affect our team\'s' \
               ' performance in the leagues we compete in. Since this is the first time, this is just a friendly ' \
               'warning that this violates our timeout policy linked below.\n' \
               'Any future breaches will incur a strike, two of which will mean your team membership will likely ' \
               'be cancelled, so please have a read of the timeout policy at ' \
               'https://www.chess.com/clubs/forum/view/team-australia-timeout-policy.\n' \
               'ZenPossum (admin)'
    elif offences == 1:
        return 'Dear Team Australia member\n' \
               'We note that you have recently timed out or resigned early in your game(s) in our match against ' \
               f'{match_opponent}. ' \
               'We understand that keeping up to date with games can be difficult, but it does affect our team\'s' \
               ' performance in the leagues we compete in. Since this is not the first time, a strike has been ' \
               'recorded against your name for violating our timeout policy linked below.\n' \
               'Any future breaches will incur a second strike, which will mean your team membership will likely ' \
               'be cancelled, so please have a read of the timeout policy at ' \
               'https://www.chess.com/clubs/forum/view/team-australia-timeout-policy.\n' \
               'ZenPossum (admin)'
    elif offences == 2:
        print(f'Please review user {username} for banning.')
        return 'Dear Team Australia member\n' \
               'We note that you have recently timed out or resigned early in your game(s) in our match against ' \
               f'{match_opponent}. ' \
               'We understand that keeping up to date with games can be difficult, but it does affect our team\'s' \
               ' performance in the leagues we compete in. Since this is not the first time, a strike has been ' \
               'recorded against your name for violating our timeout policy linked below.\n' \
               'Unfortunately, this is your second strike, which will mean your team membership will be reviewed ' \
               'by an admin and likely cancelled.\n' \
               'ZenPossum (admin)\n' \
               'Timeout policy can be found at https://www.chess.com/clubs/forum/view/team-australia-timeout-policy'
    else:
        raise ValueError


def send_message(username, text, delay=12):
    # SEND_MESSAGE defines the message sequence
    try:
        driver.switch_to.frame('mce_0_ifr')  # Switch frames for rich text editor
        # MESSAGE SEQUENCE HERE
        write_plain_text(text)
        driver.switch_to.default_content()  # Switch back
        driver.find_element(By.ID, 'message-submit').click()  # Send message
        print(f'Sent message to {username}.')
        time.sleep(delay)
    except [common.exceptions.ElementNotInteractableException, common.exceptions.NoSuchElementException]:
        # If user cannot be messaged
        print(f'Unable to message {username}.')
        blocked_users.append(name)


# Download the matches started after `matches_since`
club_members = get_all_members(club)
all_matches = get_club_matches(club, tts=delay).json['matches']['in_progress']
match_ids = [m['@id'].split('/')[-1] for m in all_matches
             if m['start_time'] >= matches_since
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
                               'date',
                               'strike',
                               # 'link',
                               'contacted'])
    print('New database created')
df['date'] = pd.to_datetime(df['date'])

# Do the same for matches to ignore
try:
    with open(ignore_matches_json_name, 'r') as file:
        ignore_matches = json.load(file)
except FileNotFoundError:
    ignore_matches = []
match_ids = [m for m in match_ids if m not in ignore_matches]

M = len(match_ids)
m = 1  # Counter for match number
for match_id in match_ids:
    # Get the match data from the API
    match_details = get_team_match(match_id, tts=delay).json['match']
    teams = match_details['teams']

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
        if username not in club_members:
            # If player is no longer in the club
            continue
        board = player['board'].split('/')[-1]
        for colour in ['white', 'black']:
            # Check if (username, match, colour) combination already appears in `df`
            if not ((df['username'] == username) &
                    (df['match'] == int(match_id)) &
                    (df['colour'] == colour)).any():
                try:
                    result = player[f'played_as_{colour}']
                except KeyError:
                    # This is if the games are still ongoing
                    continue
                if result == 'timeout' or result == 'resigned':
                    # Get more details about the game
                    board_details = get_team_match_board(match_id, board, tts=delay).json['match_board']
                    opponent = [u for u in board_details['board_scores'].keys() if u != username][0]
                    for g in board_details['games']:
                        url_given = isinstance(g[colour], str)
                        # Sometimes the player is given as an API URL instead of a dictionary
                        if url_given:
                            if g[colour].split('/')[-1] == username:
                                game = g
                        elif g[colour]['username'].lower() == username:
                            game = g
                    number_of_moves = int(game['fen'].split()[-1])
                    end_date = datetime.fromtimestamp(game['end_time'])
                    resigned_early = (result == 'resigned') and \
                                     (number_of_moves < 10) and \
                                     not is_losing(colour, game['fen'])
                    if result == 'timeout' or resigned_early:
                        # Determine number of strikes in the past 12 months
                        twelve_months_ago = datetime.today() - relativedelta(months=12)
                        year_df = df[(df['date'] >= twelve_months_ago) &  # From last 12 months &
                                     ~((df['username'] == username) & (df['match'] == match_id))]  # From another match
                        strike = year_df.value_counts(subset=['username', 'match']) \
                            .get(username, pd.Series(dtype=float)).count()

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
                            'date': [end_date],
                            'strike': [strike],
                            # 'link': [link],
                            'contacted': [False]
                        })
                        df = pd.concat([df, df_to_add], ignore_index=True)
        n += 1
    # Record finished matches
    if match_details['status'] == 'finished':
        ignore_matches.append(match_id)
    m += 1

# Messaging loop
df['first_of_two'] = ~df[['username', 'strike']].duplicated(keep='first')
'''
login()
blocked_users = []
for index, row in df.iterrows():
    if not row['contacted'] and row['first_of_two']:
        username = row['username']
        fill_recipient(username)
        message = message_text(username, row['match_opponent'], row['strike'])
        send_message(username, message, delay=15)
        new_message()
    df.at[index, 'contacted'] = True

# Display list of blocked users
print('Messaging finished.')
if blocked_users:
    print('All users messaged except for the following:')
    for user in blocked_users:
        print(user)
else:
    print('All users messaged.')
'''
# Save the collected data
df.drop('first_of_two', axis=1, inplace=True)
df.to_csv(csv_name, index=False)
with open(ignore_matches_json_name, 'w') as file:
    json.dump(ignore_matches, file)
print(f'Program finished. Data saved as {csv_name}.')

# TODO: insert Jim's existing strike data to start of df
# TODO: combine data in a sensible way
# TODO: integrate with google sheets to update rather than just list
# TODO: first round of messaging
