# ======================================================================================================================
# VoteCaptain.py formats 'don't vote yet' and 'vote now' messages on a Vote Chess game. It requires an up-to-date chrome
# driver (https://chromedriver.chromium.org/downloads) and valid Chess.com login credentials. Written by ZenPossum :)
# ======================================================================================================================

import re
from HermesBot import *

options = Options()
options.add_argument(
    'user-agent=TeamAustraliaAdminScripts '
    'Contact me at aidan.cash93@gmail.com'
)


def dont_vote_yet(game_id):
    # DONT_VOTE_YET logs in and posts a 'don't vote yet' image with a footer
    url = f'https://www.chess.com/votechess/game/{game_id}'
    login_url = f'https://www.chess.com/login_and_go?returnUrl={url}'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    set_driver(driver)
    driver.get(login_url)
    time.sleep(1)
    login_boxes = driver.find_elements(By.CLASS_NAME, 'cc-input-component')
    login_boxes[1].send_keys(username)
    login_boxes[2].send_keys(password)
    driver.find_element(By.ID, 'login').click()
    time.sleep(5)
    driver.switch_to.frame('mce_0_ifr')  # Switch frames for rich text editor
    insert_image('https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/ZenPossum/phpbIA36b.png')
    write_plain_text('New to vote chess? Read the guidelines here.\n'
                     'https://www.chess.com/clubs/forum/view/team-australia-vote-chess-guidelines-1 ')
    driver.switch_to.default_content()  # Switch back
    driver.find_element(By.ID, 'message-submit').click()  # Post message
    driver.close()


def vote_now(game_id, moves):
    # VOTE_NOW logs in and posts a 'vote now' image with the authorised moves and a footer
    url = f'https://www.chess.com/votechess/game/{game_id}'
    login_url = f'https://www.chess.com/login_and_go?returnUrl={url}'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    set_driver(driver)
    driver.get(login_url)
    time.sleep(1)
    login_boxes = driver.find_elements(By.CLASS_NAME, 'cc-input-component')
    login_boxes[1].send_keys(username)
    login_boxes[2].send_keys(password)
    driver.find_element(By.ID, 'login').click()
    time.sleep(5)
    driver.switch_to.frame('mce_0_ifr')  # Switch frames for rich text editor
    insert_image('https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/ZenPossum/php6Kg5Xp.png')
    write_plain_text('New to vote chess? Read the guidelines here.')
    shift_enter()
    write_plain_text('https://www.chess.com/clubs/forum/view/team-australia-vote-chess-guidelines-1 ')
    driver.find_element(By.ID, 'tinymce').send_keys(Keys.ARROW_LEFT*124)
    change_font_size(36)
    write_bold_text(moves.pop(0))
    for move in moves:
        write_plain_text(' or ')
        write_bold_text(move)
    write_plain_text('\n')
    driver.switch_to.default_content()  # Switch back
    driver.find_element(By.ID, 'message-submit').click()  # Post message
    driver.close()


if __name__ == '__main__':
    # Game codes
    game_codes = {
        'Deutsch': 311723,
        'Spain': 325815,
        'Turk': 334523
    }
    games = list(game_codes.keys())
    N = len(games)

    # Input loop
    print('Welcome to the Vote Captain Assistant.')
    while True:
        # Select message to post
        message_selection = input('Please select a message:\n'
                                  '[1]  Don\'t vote yet\n'
                                  '[2]  Vote now\n'
                                  '[3]  End program\n')
        message_selection = message_selection.strip(' \n[]').lower()

        if message_selection in ['1', 'd', '2', 'v']:
            # Select game to post in
            game_selection = input('Please select a game:\n' +
                                   ''.join([f'[{n}]  {games[n]}\n' for n in range(N)]) +
                                   f'[{N}]  Enter game code manually\n')
            game_selection = game_selection.strip(' \n[]').capitalize()

            # Validate game selection
            if game_selection in [str(N), 'E']:
                # If user wants to enter game code manually
                try:
                    code = int(input('Please enter the game code (https://www.chess.com/votechess/game/######):\n')
                               .strip())
                except ValueError:
                    print('Invalid selection.')
                    time.sleep(1)
                    continue
            elif game_selection in games:
                # If user provides the game name directly
                code = game_codes[game_selection]
            else:
                try:
                    # If user provides the selection number
                    code = game_codes[games[int(game_selection)]]
                except (ValueError, TypeError, IndexError):
                    print('Invalid selection.')
                    time.sleep(1)
                    continue

            if message_selection in ['1', 'd']:
                # Don't vote yet
                print(f'dont_vote_yet({code})')
                print(f'"Don\'t vote yet" message posted for game {code}')
            elif message_selection in ['2', 'v']:
                # Vote now
                moves_selection = input('Please enter the authorised moves, separated by commas (e.g. O-O, Nxf7+):\n')
                moves_selection = [m.strip() for m in moves_selection.split(',')]
                # Validate move
                all_valid = True
                pattern = re.compile(
                    r'^([PNBRQK]?[a-h]?[1-8]?[xX-]?[a-h][1-8](=[NBRQ]| ?e\.p\.)?|^O-O(?:-O)?)[+#$]?$'
                )
                for move in moves_selection:
                    if not bool(pattern.match(move)):
                        print(f'{move} is not a valid move in algebraic notation.')
                        all_valid = False
                if not all_valid:
                    time.sleep(1)
                    continue

                print(f'vote_now({code}, {moves_selection})')
                print(f'"Vote now" message posted for game {code} with moves {moves_selection}')
        elif message_selection in ['3', 'e']:
            print('Ending program')
            quit()
        else:
            print('Invalid selection.')
            time.sleep(1)
            continue
