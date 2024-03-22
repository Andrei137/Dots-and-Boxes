import time
from .board import Board
from gui.graphics import Graphics
from ai.alpha_beta import Alpha_Beta
from misc import input_handler, heart, Algorithm, Difficulty


class Game:
    # Singleton class
    instance = None

    # The game board
    game_board = Board()

    # Settings
    algorithm     = Algorithm.ALPHA_BETA  # Algorithm enum
    difficulty    = Difficulty.MEDIUM  # Difficulty enum
    player_symbol = Board.max_symbol  # max first, min second
    pvp           = False  # PvP or PvE
    gui           = True  # GUI or CLI

    # Singleton class
    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls.__new__(cls)
        return cls.instance

    # The actual board representation
    @staticmethod
    def __str__():
        return str(Game.game_board)

    # Bitset representation of the board
    @staticmethod
    def __repr__():
        return repr(Game.game_board)

    # Resets the game
    @staticmethod
    def reset():
        Game.game_board    = Board()
        Game.completed_box = False

    # Quits the game, printing a heart if exiting from the main menu
    @staticmethod
    def quit(print_heart=False):
        input_handler.clear_screen()
        if print_heart:
            heart.Heart().print_full_heart()
        exit(0)

    # Returns a string with the current player
    @staticmethod
    def print_current_player():
        if Game.pvp:
            # if the game mode is PvP, print player X or player O
            print(f"Current player: {Game.game_board.current_player}", end="\n\n")
        else:
            # if the game mode is PvE, return the player or the computer
            if Game.game_board.current_player == Game.player_symbol:
                print(f"Player's turn")
            else:
                print("Computer is thinking", end='')

                # Loading effect
                for _ in range(3):
                    print(".", end='', flush=True)
                    time.sleep(0.25)

    # Gets a point position from the user
    @staticmethod
    def get_coordinates_from_user():
        input_handler.clear_screen()
        print(Game.get_instance())

        try:
            Game.print_current_player()
            print("[0] Back")
            print("[?] Select a point (line-column)")
            position = input("\n-> ")

            # go back to main menu
            if position == '0':
                Game.reset()
                Game.main_menu()
            else:
                i, j = position.split('-')
                if not i.isdigit() or not j.isdigit() or not Game.game_board.valid_position(int(i) - 1, int(j) - 1):
                    Game.get_coordinates_from_user()
                Game.get_direction_from_user(int(i) - 1, int(j) - 1)
            return None

        except ValueError:
            Game.get_coordinates_from_user()
        except (KeyboardInterrupt, EOFError):
            Game.quit()

    # Gets a direction from the user, from the previously selected point
    @staticmethod
    def get_direction_from_user(i, j):
        input_handler.clear_screen()
        print(Game.get_instance())

        Game.print_current_player()
        print(f"Point: {i + 1}-{j + 1} ")
        print("[0] Back")

        board = Game.game_board
        options = board.get_direction_options(i, j)

        # if it didn't find a possible direction from the current point, ask the user for another one
        if len(options) == 0:
            Game.get_coordinates_from_user()
        # if there is only one option, make the move, no point asking the user to input it too
        elif options.count("or") == 0:
            # remove the [] from the string
            direction = options[1] + options[3:]

            board.make_move(i, j, direction)
        else:
            # let the user choose the direction
            print("[?] Select a direction (" + options + ") ")
            try:
                direction = input("\n-> ")

                # go back to main menu
                if direction == '0':
                    Game.get_coordinates_from_user()
                else:
                    # place the first letter between []
                    direction_temp = '[' + direction[0] + ']' + direction[1:]
                    if not any(option.startswith(direction_temp) for option in options.split(' or ')) or direction == '':
                        Game.get_direction_from_user(i, j)

                    board.make_move(i, j, direction)
            except (KeyboardInterrupt, EOFError):
                Game.quit()

    # Prints the final score and the winner, also waits for input to continue
    # For the GUI, that input means quitting the window
    # For the CLI, that input means pressing any key to continue
    @staticmethod
    def print_result(boxes=[]):
        input_handler.clear_screen()

        board = Game.game_board

        if not Game.gui:
            print(Game.get_instance(), end="\n\n")

        print(f"Player {Board.max_symbol}: " + str(board.max_score) + " points")
        print(f"Player {Board.min_symbol}: " + str(board.min_score) + " points", end="\n\n")

        if board.max_score == board.min_score:
            print("It's a tie!")
        else:
            print("Player " + (f"{Board.max_symbol}" if board.max_score > board.min_score else f"{Board.min_symbol}") + " won!")

        if Game.gui:
            Graphics().player_click(Game.get_instance(), boxes, True)
            Graphics().quit_graphics()

        else:
            try:
                _ = input("\nPress any key to continue...")
            except KeyboardInterrupt:
                Game.quit()

    # Starts the game, looping until it's finished
    @staticmethod
    def play():
        game = Game.get_instance()
        board = game.game_board

        if Game.gui:
            boxes = Graphics().start_graphics(game)

        while not Game.game_board.is_finished():
            input_handler.clear_screen()
            Game.print_current_player()

            if not Game.pvp and board.current_player != Game.player_symbol:
                if Game.algorithm == Algorithm.ALPHA_BETA:
                    time1 = time.time()
                    i, j, direction = Alpha_Beta.get_move(game.game_board)
                    time2 = time.time()

                    
                board.make_move(i, j, direction)
                if Game.gui:
                    boxes = Graphics().display_game_board(game)

                if abs(time2 - time1) > 0.01:
                    input_handler.clear_screen()
                    print(f"Computer thought for {time2 - time1:.2f} seconds")
                    time.sleep(1)
            else:
                if Game.gui:
                    score = 0

                    valid_move = False

                    while not valid_move:
                        try:
                            i, j = Graphics().player_click(game, boxes)

                            if i == j and i is None:
                                Graphics().quit_graphics()
                                Game.reset()
                                Game.main_menu()
                            elif not (j & 1):
                                valid_move = board.make_move(i // 2, j // 2, "down")
                                boxes = Graphics().display_game_board(game)
                            else:
                                valid_move = board.make_move(i // 2, j // 2, "right")
                                boxes = Graphics().display_game_board(game)

                            boxes = Graphics().display_game_board(game)
                        except KeyboardInterrupt:
                            Graphics().quit_graphics()
                            Game.reset()
                            Game.main_menu()
                else:
                    Game.get_coordinates_from_user()

            if not board.completed_box:
                board.current_player = board.get_opponent()

        if Game.gui:
            Game.print_result(boxes)
        else:
            Game.print_result()

        Game.reset()

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
                Alpha_Beta.set_difficulty(str(Game.difficulty))
        except KeyboardInterrupt:
            Game.quit()

    # Changes the game_board size
    @staticmethod
    def change_game_board_sizes():
        try:
            option = input_handler.get_valid_input("< Choose the number of dots per line >", '', True)

            if option != '0':
                # first change the line numbers
                Board.no_lines = int(option)

                try:
                    option = input_handler.get_valid_input("< Choose the number of dots per column >", '', True, Board.no_lines)

                    if option != '0':
                        # then change the column number
                        Board.no_columns = int(option)
                except KeyboardInterrupt:
                    Game.quit()

            if Game.gui:
                # in case the game_board size changes, reset the width and height of the window
                Graphics.update_width_height(Game.get_instance())

            Game.reset()

        except KeyboardInterrupt:
            Game.quit()

    @staticmethod
    def toggle_gamemode():
        Game.pvp = not Game.pvp

    # Changes the starting player
    @staticmethod
    def switch_starting_player():
        Game.player_symbol = Board.min_symbol if Game.player_symbol == Board.max_symbol else Board.max_symbol

    # Toggles the GUI
    @staticmethod
    def toggle_gui():
        Game.gui = not Game.gui

        if Game.gui:
            # if the GUI is turned on, reset the width and height of the window in case they were changed
            Graphics.update_width_height(Game.get_instance())

    # Displays the logo of the game
    @staticmethod
    def logo():
        return " _____        _                  ____                            \n" + \
               "|  __ \\      | |         ___    |  _ \\                         \n" + \
               "| |  | | ___ | |_ ___   ( _ )   | |_) | _____  _____  ___        \n" + \
               "| |  | |/ _ \\| __/ __|  / _ \\/\\ |  _ < / _ \\ \\/ / _ \\/ __| \n" + \
               "| |__| | (_) | |_\\__ \\ | (_>  < | |_) | (_) >  <  __/\\__ \\   \n" + \
               "|_____/ \\___/ \\__|___/  \\___/\\/ |____/ \\___/_/\\_\\___||___/\n"

    @staticmethod
    def main_menu_pvp():
        options = "Start game, " + \
                  "Change the board sizes (" + str(Board.no_lines) + "x" + str(Board.no_columns) + "), " + \
                  "Choose the game type (Pv" + ("P" if Game.pvp else "E") + "), " + \
                  "Toggle GUI (" + ("On" if Game.gui else "Off") + "), " + \
                  "Quit"

        try:
            option = input_handler.get_valid_input(Game.logo() + "\n\n< Choose an option >", options)

            if option == '0':
                Game.quit(True)
            else:
                if option == '1':
                    Game.play()
                elif option == '2':
                    Game.change_game_board_sizes()
                elif option == '3':
                    Game.toggle_gamemode()
                elif option == '4':
                    Game.toggle_gui()

                Game.main_menu()
        except KeyboardInterrupt:
            Game.quit()

    @staticmethod
    def main_menu_pve():
        options = "Start game, " + \
                  "Change the computer's algorithm (" + str(Game.algorithm) + "), " + \
                  "Change difficulty (" + str(Game.difficulty) + "), " + \
                  "Change the board sizes (" + str(Board.no_lines) + "x" + str(Board.no_columns) + "), " + \
                  "Choose the game type (Pv" + ("P" if Game.pvp else "E") + "), " + \
                  "Toggle GUI (" + ("On" if Game.gui else "Off") + "), " + \
                  "Quit"

        try:
            option = input_handler.get_valid_input(Game.logo() + "\n\n< Choose an option >", options)

            if option == '0':
                Game.quit(True)
            else:
                if option == '1':
                    Game.play()
                elif option == '2':
                    Game.change_algorithm()
                elif option == '3':
                    Game.change_difficulty()
                elif option == '4':
                    Game.change_game_board_sizes()
                elif option == '5':
                    Game.toggle_gamemode()
                elif option == '6':
                    Game.toggle_gui()

                Game.main_menu()
        except KeyboardInterrupt:
            Game.quit()

    # Prints the game menu and gets an option from the user
    @staticmethod
    def main_menu():
        if Game.pvp:
            Game.main_menu_pvp()
        else:
            Game.main_menu_pve()
