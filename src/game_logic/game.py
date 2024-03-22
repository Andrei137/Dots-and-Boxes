from . import board
from gui import graphics
from ai import alpha_beta
from misc import input_handler, heart, Algorithm, Difficulty
from copy import deepcopy


class Game:
    instance = None  # Singleton class

    # Settings
    algorithm             = Algorithm.ALPHA_BETA  # Algorithm enum
    difficulty            = Difficulty.MEDIUM  # Difficulty enum
    player_symbol         = board.Board.max_symbol  # max first, min second
    pvp                   = False  # pvp or pve
    gui                   = True  # bool toggle

    # The game board
    game_board = board.Board()

    # Singleton class
    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls.__new__(cls)
        return cls.instance

    # Represents the current state of the game
    def __str__(self):
        return str(self.game_board)

    def __repr__(self):
        return repr(self.game_board)

    # Resets the game
    @staticmethod
    def reset():
        Game.game_board                 = board.Board()
        Game.completed_box              = False
        Game.max_score = Game.min_score = 0

    # Quits the game, printing a heart if exiting from the main menu
    @staticmethod
    def quit(print_heart=False):
        input_handler.clear_screen()
        if print_heart:
            heart.Heart().print_full_heart()
        exit(0)

    @staticmethod
    def get_current_player():
        if Game.pvp:
            return f"Current player: {Game.game_board.current_player}"
        else:
            if Game.game_board.current_player == Game.player_symbol:
                return f"Player's turn"
            else:
                return f"Computer's turn"

    # Gets a point position from the user
    @staticmethod
    def get_coordinates_from_user():
        input_handler.clear_screen()
        print(Game.get_instance())

        try:
            print(Game.get_current_player(), end="\n\n")
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

    @staticmethod
    def get_direction_from_user(i, j):
        input_handler.clear_screen()
        print(Game.get_instance())

        print(Game.get_current_player(), end="\n\n")
        print(f"Point: {i + 1}-{j + 1} ")
        print("[0] Back")

        options = Game.game_board.get_direction_options(i, j)

        # if we didn't find a possible direction from the current point, ask the user for another one
        if len(options) == 0:
            Game.get_coordinates_from_user()
        # if we only have one option, make the move, no point asking the user to input it too
        elif options.count("or") == 0:
            # remove the [] from the string
            direction = options[1] + options[3:]

            Game.game_board.make_move(i, j, direction)
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

                    Game.game_board.make_move(i, j, direction)
            except (KeyboardInterrupt, EOFError):
                Game.quit()

    # Prints the final score and the winner, also waits for input to continue
    @staticmethod
    def print_result(boxes=[]):
        input_handler.clear_screen()

        if not Game.gui:
            print(Game.get_instance(), end="\n\n")

        print(f"Player {board.Board.max_symbol}: " + str(Game.game_board.max_score) + " points")
        print(f"Player {board.Board.min_symbol}: " + str(Game.game_board.min_score) + " points", end="\n\n")

        if Game.game_board.max_score == Game.game_board.min_score:
            print("It's a tie!")
        else:
            print("Player " + (f"{board.Board.max_symbol}" if Game.game_board.max_score > Game.game_board.min_score else f"{board.Board.min_symbol}") + " won!")

        if Game.gui:
            graphics.Graphics().player_click(Game.get_instance(), boxes, True)
            graphics.Graphics().quit_graphics()

        else:
            try:
                _ = input("\nPress any key to continue...")
            except KeyboardInterrupt:
                Game.quit()

    # Starts the game, looping until it's finished
    @staticmethod
    def play():
        game = Game.get_instance()

        if Game.gui:
            boxes = graphics.Graphics().start_graphics(game)

        while not Game.game_board.is_finished():
            input_handler.clear_screen()
            print(Game.get_current_player())

            if not Game.pvp and Game.game_board.current_player != Game.player_symbol:
                if Game.algorithm == Algorithm.ALPHA_BETA:
                    i, j, direction = alpha_beta.Alpha_Beta.get_move(game.game_board)
                Game.game_board.make_move(i, j, direction)
                if Game.gui:
                    boxes = graphics.Graphics().display_game_board(game)
            else:
                if Game.gui:
                    score = 0

                    valid_move = False

                    while not valid_move:
                        try:
                            i, j = graphics.Graphics().player_click(game, boxes)

                            if i == j and i is None:
                                graphics.Graphics().quit_graphics()
                                Game.reset()
                                Game.main_menu()
                            elif not (j & 1):
                                valid_move = Game.game_board.make_move(i // 2, j // 2, "down")
                                boxes = graphics.Graphics().display_game_board(game)
                            else:
                                valid_move = Game.game_board.make_move(i // 2, j // 2, "right")
                                boxes = graphics.Graphics().display_game_board(game)

                            boxes = graphics.Graphics().display_game_board(game)
                        except KeyboardInterrupt:
                            graphics.Graphics().quit_graphics()
                            Game.reset()
                            Game.main_menu()
                else:
                    Game.get_coordinates_from_user()

            if not Game.game_board.completed_box:
                Game.game_board.current_player = Game.game_board.get_opponent()

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
                alpha_beta.Alpha_Beta.set_difficulty(str(Game.difficulty))
        except KeyboardInterrupt:
            Game.quit()

    # Changes the game_board size
    @staticmethod
    def change_game_board_sizes():
        try:
            option = input_handler.get_valid_input("< Choose the number of dots per line >", board_menu=True)

            if option != '0':
                # first change the line numbers
                board.Board.no_lines = int(option)

                try:
                    option = input_handler.get_valid_input("< Choose the number of dots per column >", board_menu=True)

                    if option != '0':
                        # then change the column number
                        board.Board.no_columns = int(option)
                except KeyboardInterrupt:
                    Game.quit()
        except KeyboardInterrupt:
            Game.quit()

    # Changes the starting player
    @staticmethod
    def change_starting_player():
        Game.player_symbol = board.Board.min_symbol if Game.player_symbol == board.Board.max_symbol else board.Board.max_symbol

    # Toggles the GUI
    @staticmethod
    def toggle_gui():
        Game.gui = not Game.gui

        if Game.gui:
            # if we turn the GUI on, we need to reset the width and height of the window in case they were changed
            graphics.Graphics.update_width_height(Game.get_instance())

    # display the logo of the project
    @staticmethod
    def logo():
        return " _____        _                  ____                            \n" + \
               "|  __ \\      | |         ___    |  _ \\                         \n" + \
               "| |  | | ___ | |_ ___   ( _ )   | |_) | _____  _____  ___        \n" + \
               "| |  | |/ _ \\| __/ __|  / _ \\/\\ |  _ < / _ \\ \\/ / _ \\/ __| \n" + \
               "| |__| | (_) | |_\\__ \\ | (_>  < | |_) | (_) >  <  __/\\__ \\   \n" + \
               "|_____/ \\___/ \\__|___/  \\___/\\/ |____/ \\___/_/\\_\\___||___/\n"

    # Prints the game menu and gets an option from the user
    @staticmethod
    def main_menu():
        options = "Start game, " \
                + "Change the computer's algorithm (" + str(Game.algorithm) + "), " \
                + "Change difficulty (" + str(Game.difficulty) + "), " \
                + "Change the board sizes (" + str(board.Board.no_lines) + "x" + str(board.Board.no_columns) + "), " \
                + "Choose the game type (Pv" + ("P" if Game.pvp else "E") + "), "
        if not Game.pvp:
            options += "Switch starting player (" + ("Player" if Game.player_symbol == board.Board.max_symbol else "Computer") + " goes first), "
        options +="Toggle GUI (" + ("On" if Game.gui else "Off") + "), " \
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
                    Game.change_game_board_sizes()

                    if Game.gui:
                        # in case we change the game_board size, we need to reset the width and height of the window
                        graphics.Graphics.update_width_height(Game.get_instance())
                    Game.game_board = board.Board()

                    Game.reset()
                elif option == '5':
                    Game.pvp = not Game.pvp
                elif option == '6':
                    if not Game.pvp:
                        Game.change_starting_player()
                    else:
                        Game.toggle_gui()
                elif not Game.pvp and option == '7':
                    Game.toggle_gui()

                Game.main_menu()
        except KeyboardInterrupt:
            Game.quit()
