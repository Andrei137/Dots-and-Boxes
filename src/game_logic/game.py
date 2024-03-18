from . import box
from gui import graphics
from misc import input_handler, heart, Algorithm, Difficulty


class Game:
    instance = None  # Singleton class

    # Settings
    algorithm     = Algorithm.ALPHA_BETA  # Algorithm enum
    difficulty    = Difficulty.MEDIUM  # Difficulty enum
    no_lines      = no_columns = 4  # min 3, max 8
    player_symbol = 'X'  # X first, O second
    gui           = True  # bool toggle

    # Current match info
    current_player = 'X'
    filled_box     = False  # Keeps turn if True
    score_X        = 0
    score_O        = 0

    # Singleton class
    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls.__new__(cls)
            cls.board    = [[box.Box() for _ in range(Game.no_columns)] for _ in range(Game.no_lines)]
        return cls.instance

    # Resets the game
    @classmethod
    def reset(cls):
        # resetting the instance will cause the board to reset
        cls.instance                = None
        Game.current_player         = 'X'
        Game.filled_box             = False
        Game.score_X = Game.score_O = 0

    @staticmethod
    def quit(print_heart=False):
        input_handler.clear_screen()
        if print_heart:
            heart.Heart().print_full_heart()
        exit(0)

    # Represents the current state of the game
    def __str__(self):
        board = ''
        for i in range(Game.no_lines - 1):
            for j in range(Game.no_columns - 1):
                # checks for the up line
                board += '*---' if self.board[i][j].up else '*   '
            board += '*\n'

            for j in range(Game.no_columns - 1):
                # checks for the left line
                board += '|' if self.board[i][j].left else ' '

                board += ' ' + self.board[i][j].symbol + ' '

            # last column -> checks right instead of left
            board += ('|' if self.board[i][Game.no_columns - 2].right else ' ') + '\n'

        # last line -> checks down instead of up
        for j in range(Game.no_columns - 1):
            board += '*---' if self.board[Game.no_lines - 2][j].down else '*   '

        # last point
        return board + '*'

    # Returns true if the box position (i, j) is valid
    @staticmethod
    def valid_position(i, j):
        return 0 <= i < Game.no_lines and 0 <= j < Game.no_columns

    # Checks if the box (i, j) is completed and updates the score, keeping the turn if True
    @staticmethod
    def check_box_completed(i, j):
        game = Game.get_instance()

        if game.board[i][j].complete_box():
            game.filled_box = True
            game.board[i][j].symbol = game.current_player

            if game.current_player == 'X':
                game.score_X += 1
            else:
                game.score_O += 1

    # Returns true if the game is finished
    @staticmethod
    def is_finished():
        game = Game.get_instance()
        return game.score_X + game.score_O == (Game.no_lines - 1) * (Game.no_columns - 1)

    # Prints the final score and the winner, also waits for input to continue
    @staticmethod
    def print_result(boxes=[]):
        game = Game.get_instance()

        input_handler.clear_screen()

        if not Game.gui:
            print(game, end="\n\n")

        print("Player X: " + str(game.score_X) + " points")
        print("Player O: " + str(game.score_O) + " points", end="\n\n")
        game = Game.get_instance()
        if game.score_X == game.score_O:
            print("It's a tie!")
        else:
            print("Player " + ('X' if game.score_X > game.score_O else 'O') + " won!")

        if Game.gui:
            graphics.Graphics().player_click(game, boxes, True)
            graphics.Graphics().quit_graphics()

        else:
            try:
                _ = input("\nPress any key to continue...")
            except KeyboardInterrupt:
                Game.quit()

        Game.reset()

    @staticmethod
    def find_direction_options(i, j):
        game = Game.get_instance()
        options = ''

        # when going up from the point (i, j), we are adding the left line of the box (i - 1, j)
        if i > 0 and not game.board[i - 1][j].left:
            options += "[u]p or "
        # when going down from the point (i, j), we are adding the left line of the box (i, j)
        if i < Game.no_lines - 1 and not game.board[i][j].left:
            options += "[d]own or "
        # when going left from the point (i, j), we are adding the up line of the box (i, j - 1)
        if j > 0 and not game.board[i][j - 1].up:
            options += "[l]eft or "
        # when going right from the point (i, j), we are adding the up line of the box (i, j)
        if j < Game.no_columns - 1 and not game.board[i][j].up:
            options += "[r]ight or "

        return options

    @staticmethod
    def get_direction_from_user(i, j):
        game = Game.get_instance()
        input_handler.clear_screen()
        print(game)

        print(f"\nCurrent player: {game.current_player}", end="\n\n")
        print(f"Point: {i + 1}-{j + 1} ")
        print("[0] Back")

        options = Game.find_direction_options(i, j)

        # if we didn't find a possible direction from the current point, ask the user for another one
        if len(options) == 0:
            Game.get_coordinates_from_user()
        # if we only have one option, make the move, no point asking the user to input it too
        elif options.count('or') == 1:
            # remove the [] from the string
            direction = options[1] + options[3:]

            Game.make_move(i, j, direction[:-4])
        else:
            # let the user choose the direction
            print("[?] Select a direction (" + options[:-4] + ") ")
            try:
                direction = input("\n-> ")

                # go back to main menu
                if direction == '0':
                    Game.reset()
                    Game.main_menu()

                # place the first letter between []
                direction_temp = '[' + direction[0] + ']' + direction[1:]
                if not any(option.startswith(direction_temp) for option in options.split(' or ')) or direction == '':
                    Game.get_direction_from_user(i, j)

                Game.make_move(i, j, direction)
            except (KeyboardInterrupt, EOFError):
                Game.quit()


    # Gets a point position from the user
    @staticmethod
    def get_coordinates_from_user():
        game = Game.get_instance()
        input_handler.clear_screen()
        print(game)

        try:
            print(f"\nCurrent player: {game.current_player}", end="\n\n")
            print("[0] Back")
            print("[?] Select a point (line-column)")
            position = input("\n-> ")

            # go back to main menu
            if position == '0':
                Game.reset()
                Game.main_menu()
            else:
                i, j = position.split('-')
                if not i.isdigit() or not j.isdigit() or not Game.valid_position(int(i) - 1, int(j) - 1):
                    Game.get_coordinates_from_user()
                Game.get_direction_from_user(int(i) - 1, int(j) - 1)
            return None

        except ValueError:
            Game.get_coordinates_from_user()
        except (KeyboardInterrupt, EOFError):
            Game.quit()

    # Makes a move on the board, marking both boxes and checking for completed boxes
    # For the GUI -> If the move was already made, returns False so we don't change the player
    @staticmethod
    def make_move(i, j, direction):
        game = Game.get_instance()
        game.filled_box = False

        if "right".startswith(direction):
            # the up-left point (i, j) represents the box (i, j)
            if game.board[i][j].up is True:
                return False

            game.board[i][j].up = True
            Game.check_box_completed(i, j)

            if Game.valid_position(i - 1, j):
                game.board[i - 1][j].down = True
                Game.check_box_completed(i - 1, j)
        elif "down".startswith(direction):
            # the up-left point (i, j) represents the box (i, j)
            if game.board[i][j].left is True:
                return False

            game.board[i][j].left = True
            Game.check_box_completed(i, j)

            if Game.valid_position(i, j - 1):
                game.board[i][j - 1].right = True
                Game.check_box_completed(i, j - 1)
        elif "left".startswith(direction):
            # the up-right point (i, j) represents the box (i, j - 1)
            if game.board[i][j - 1].up is True:
                return False

            game.board[i][j - 1].up = True
            Game.check_box_completed(i, j - 1)

            if Game.valid_position(i - 1, j - 1):
                game.board[i - 1][j - 1].down = True
                Game.check_box_completed(i - 1, j - 1)
        elif "up".startswith(direction):
            # the down-left point (i, j) represents the box (i - 1, j)
            if game.board[i - 1][j].left is True:
                return False

            game.board[i - 1][j].left = True
            Game.check_box_completed(i - 1, j)

            if Game.valid_position(i - 1, j - 1):
                game.board[i - 1][j - 1].right = True
                Game.check_box_completed(i - 1, j - 1)

        # not a repeated move
        return True

    # Starts the game, looping until it's finished
    @staticmethod
    def play():
        game = Game.get_instance()

        if Game.gui:
            boxes = graphics.Graphics().start_graphics(game)

        while not Game.is_finished():
            if Game.gui:
                input_handler.clear_screen()
                print(f"\nCurrent player: {game.current_player}", end="\n\n")

                new_line = False

                while not new_line:
                    try:
                        i, j = graphics.Graphics().player_click(game, boxes)

                        if i == j == None:
                            graphics.Graphics().quit_graphics()
                            Game.reset()
                            Game.main_menu()
                        elif not (j & 1):
                            new_line = Game.make_move(i // 2, j // 2, "down")
                        else:
                            new_line = Game.make_move(i // 2, j // 2, "right")

                        boxes = graphics.Graphics().display_game_board(game)
                    except KeyboardInterrupt:
                        graphics.Graphics().quit_graphics()
                        Game.reset()
                        Game.main_menu()
            else:
                Game.get_coordinates_from_user()

            if not game.filled_box:
                game.current_player = 'O' if game.current_player == 'X' else 'X'

        if Game.gui:
            Game.print_result(boxes)
        else:
            Game.print_result()

    # display the logo of the project
    @staticmethod
    def logo():
        return " _____        _                  ____                            \n" + \
               "|  __ \\      | |         ___    |  _ \\                         \n" + \
               "| |  | | ___ | |_ ___   ( _ )   | |_) | _____  _____  ___        \n" + \
               "| |  | |/ _ \\| __/ __|  / _ \\/\\ |  _ < / _ \\ \\/ / _ \\/ __| \n" + \
               "| |__| | (_) | |_\\__ \\ | (_>  < | |_) | (_) >  <  __/\\__ \\   \n" + \
               "|_____/ \\___/ \\__|___/  \\___/\\/ |____/ \\___/_/\\_\\___||___/\n"

    # Selects the algorithm chosen by the user
    @staticmethod
    def change_algorithm():
        options = "IDA*" + (" <-, " if Game.algorithm == Algorithm.IDA_STAR else ", ") \
                + "Alpha-Beta" + (" <-, " if Game.algorithm == Algorithm.ALPHA_BETA else ", ") \
                + "Bayesian Network" + (" <-, " if Game.algorithm == Algorithm.BAYESIAN_NETWORK else ", ") \
                + "Back"

        try:
            option = input_handler.get_valid_input("< Choose an algorithm >", options)

            if option != '0':
                Game.algorithm = Algorithm.select_algorithm(option)
        except KeyboardInterrupt:
            Game.quit()

    # Selects the difficulty chosen by the user
    @staticmethod
    def change_difficulty():
        options = "Easy" + (" <-, " if Game.difficulty == Difficulty.EASY else ", ") \
                + "Medium" + (" <-, " if Game.difficulty == Difficulty.MEDIUM else ", ") \
                + "Hard" + (" <-, " if Game.difficulty == Difficulty.HARD else ", ") \
                + "Back"

        try:
            option = input_handler.get_valid_input("< Choose a difficulty >", options)

            if option != '0':
                Game.difficulty = Difficulty.select_difficulty(option)
        except KeyboardInterrupt:
            Game.quit()

    # Changes the board size
    @staticmethod
    def change_board_sizes():
        try:
            option = input_handler.get_valid_input("< Choose the number of dots per line >", board_menu=True)

            if option != '0':
                # first change the line numbers
                Game.no_lines = int(option)

                try:
                    option = input_handler.get_valid_input("< Choose the number of dots per column >", board_menu=True)

                    if option != '0':
                        # then change the column number
                        Game.no_columns = int(option)
                except KeyboardInterrupt:
                    Game.quit()
        except KeyboardInterrupt:
            Game.quit()

    # Prints the game menu and gets an option from the user
    @staticmethod
    def main_menu():
        options = "Start game, " \
                + "Change the computer's algorithm (" + str(Game.algorithm) + "), " \
                + "Change difficulty (" + str(Game.difficulty) + "), " \
                + "Change the board size (" + str(Game.no_lines) + "x" + str(Game.no_columns) + "), " \
                + "Switch starting player (" + ("Player" if Game.player_symbol == 'X' else "Computer") + " goes first), " \
                + "Toggle GUI (" + ("On" if Game.gui else "Off") + "), " \
                + "Quit"

        try:
            option = input_handler.get_valid_input(Game.logo() + "\n\n< Choose an option >", options)

            if option == '0':
                # we exit the game and print a heart :3
                Game.quit(True)
            else:
                if option == '1':
                    Game.play()
                elif option == '2':
                    Game.change_algorithm()
                elif option == '3':
                    Game.change_difficulty()
                elif option == '4':
                    Game.change_board_sizes()

                    if Game.gui:
                        # in case we change the board size, we need to reset the width and height of the window
                        graphics.Graphics.update_width_height(Game.get_instance())

                    Game.reset()
                elif option == '5':
                    Game.player_symbol = 'X' if Game.player_symbol == 'O' else 'O'
                elif option == '6':
                    Game.gui = not Game.gui

                    if Game.gui:
                        # if we turn the GUI on, we need to reset the width and height of the window in case they were changed
                        graphics.Graphics.update_width_height(Game.get_instance())

                Game.main_menu()
        except KeyboardInterrupt:
            Game.quit()
