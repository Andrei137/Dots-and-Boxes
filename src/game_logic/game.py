import sys
import time
from os import path
from .board import Board
from ..gui.graphics import Graphics
from ..ai.alpha_beta import Alpha_Beta
from ..ai.ida_star import Ida_Star
from ..misc import input_handler, heart, Algorithm, Difficulty


class Game:
    # Singleton class
    instance = None

    # The game board
    game_board = Board()

    # For logs
    if getattr(sys, 'frozen', False):  # if the application is bundled by PyInstaller
        log_dir = path.join(sys._MEIPASS, 'logs')
    else:
        log_dir = path.join(path.dirname(__file__), '..', '..', 'logs')

    match_number = 1

    # Settings
    algorithm     = Algorithm.ALPHA_BETA  # Algorithm enum
    difficulty    = Difficulty.MEDIUM  # Difficulty enum
    player_symbol = Board.max_symbol  # max first, min second
    pvp           = False  # PvP or PvE
    gui           = True  # GUI or CLI

    depths = {
    #   (n, 2)      (n, 3)      (n, 4)      (n, 5)     (n, 6)     (n, 7)
        (2, 2):  0, (2, 3):  7, (2, 4): 10, (2, 5): 7, (2, 6): 6, (2, 7): 6,  # (2, m)
        (3, 2):  7, (3, 3):  7, (3, 4):  6, (3, 5): 5, (3, 6): 5, (3, 7): 4,  # (3, m)
        (4, 2): 10, (4, 3):  6, (4, 4):  5, (4, 5): 5, (4, 6): 4, (4, 7): 4,  # (4, m)
        (5, 2):  7, (5, 3):  5, (5, 4):  5, (5, 5): 4, (5, 6): 4, (5, 7): 3,  # (5, m)
        (6, 2):  6, (6, 3):  5, (6, 4):  4, (6, 5): 4, (6, 6): 3, (6, 7): 3,  # (6, m)
        (7, 2):  6, (7, 3):  4, (7, 4):  4, (7, 5): 3, (7, 6): 3, (7, 7): 2,  # (7, m)
    }


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
            time.sleep(0.25)
        sys.exit(0)

    # Returns a string with the current player
    @staticmethod
    def print_current_player():
        if Game.pvp:
            # if the game mode is PvP, print player X or player O
            print(f"\nCurrent player: {Game.game_board.current_player}", end="\n\n")
        else:
            # if the game mode is PvE, return the player or the computer
            if Game.game_board.current_player == Game.player_symbol:
                print(f"\nPlayer's turn")
            else:
                print("\nComputer is thinking", end='')

                # Loading effect
                for _ in range(3):
                    print(".", end='', flush=True)
                    time.sleep(0.25)

    # Quits the match
    @staticmethod
    def quit_match(graphics=True):
        if graphics:
            Graphics().quit_graphics()

        # mark the match aborted in the logs
        with open(path.join(Game.log_dir, 'time.txt'), 'a') as f:
            f.write("Aborted\n")

        with open(path.join(Game.log_dir, 'match_history.txt'), 'a') as f:
            f.write("Aborted\n")

        Game.reset()
        Game.main_menu()

    # Prints the score of the game
    @staticmethod
    def print_score():
        board = Game.game_board

        if Game.pvp:
            if board.max_score == 1:
                print(f"Player {Board.max_symbol}: 1 point")
            else:
                print(f"Player {Board.max_symbol}: " + str(board.max_score) + " points")
            if board.min_score == 1:
                print(f"Player {Board.min_symbol}: 1 point", end="\n\n")
            else:
                print(f"Player {Board.min_symbol}: " + str(board.min_score) + " points", end="\n\n")
        else:
            player_score    = board.max_score if Game.player_symbol == Board.max_symbol else board.min_score
            computer_score  = board.min_score if Game.player_symbol == Board.max_symbol else board.max_score
            computer_symbol = Board.min_symbol if Game.player_symbol == Board.max_symbol else Board.max_symbol

            if player_score == 1:
                player = f"Player   ({Game.player_symbol}): 1 point"
            else:
                player = f"Player   ({Game.player_symbol}): {player_score} points"

            if computer_score == 1:
                computer = f"Computer ({computer_symbol}): 1 point"
            else:
                computer = f"Computer ({computer_symbol}): {computer_score} points"

            # If the player is MAX, print the player's score first
            if Game.player_symbol == Board.max_symbol:
                print(player)
                print(computer, end="\n\n")
            else:
                print(computer)
                print(player, end="\n\n")

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
                Game.quit_match(False)
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

    @staticmethod
    def get_gui_move_from_user(boxes):
        game       = Game.get_instance()
        board      = Game.game_board
        valid_move = False

        while not valid_move:
            try:
                i, j = Graphics().player_click(game, boxes)

                if i == j and i is None:
                    Game.quit_match()
                elif not (j & 1):
                    valid_move = board.make_move(i // 2, j // 2, "down")
                    boxes = Graphics().display_game_board(game)
                else:
                    valid_move = board.make_move(i // 2, j // 2, "right")
                    boxes = Graphics().display_game_board(game)

                boxes = Graphics().display_game_board(game)
            except KeyboardInterrupt:
                Game.quit_match()
        return boxes

    @staticmethod
    def computer_move(computer_move_count):
        board      = Game.game_board
        time_start = time.time()

        if Game.algorithm == Algorithm.IDA_STAR:
            board.boxes = Ida_Star.get_move(board, Game.depths[(Board.no_lines, Board.no_columns)])

            # count computer's mew score
            computer_score = 0
            for i in range(Board.no_lines - 1):
                for j in range(Board.no_columns - 1):
                    if board.boxes[i][j].symbol == Ida_Star.computer_symbol:
                        computer_score += 1

            # if it is bigger than the previous score, then the computer has completed a box
            if computer_score > board.get_player_score(Ida_Star.computer_symbol):
                board.completed_box = True
                if Ida_Star.computer_symbol == Board.max_symbol:
                    board.max_score = computer_score
                else:
                    board.min_score = computer_score
            else:
                board.completed_box = False

        elif Game.algorithm == Algorithm.ALPHA_BETA:
            move = Alpha_Beta.get_move(board, Game.depths[(Board.no_lines, Board.no_columns)])

            if move is None:
                move = Alpha_Beta.get_move(board, 1)

            i, j, direction = move

            board.make_move(i, j, direction)

        timer = time.time() - time_start

        if abs(timer) > 0.01:
            with open(path.join(Game.log_dir, 'time.txt'), 'a') as f:
                if computer_move_count < 10:
                    f.write(f"Move  {computer_move_count}: {timer} seconds\n")
                else:
                    f.write(f"Move {computer_move_count}: {timer} seconds\n")
                computer_move_count += 2
        else:
            with open(path.join(Game.log_dir, 'time.txt'), 'a') as f:
                if computer_move_count < 10:
                    f.write(f"Move  {computer_move_count}: Instant\n")
                else:
                    f.write(f"Move {computer_move_count}: Instant\n")
                computer_move_count += 2
        return computer_move_count

    # Writes the result of the match in the logs
    @staticmethod
    def write_result(result, time):
        with open(path.join(Game.log_dir, 'match_history.txt'), 'a') as f:
            if Game.pvp:
                f.write(f"Players   : Player {Board.max_symbol} - Player {Board.min_symbol}\n")
                f.write(f"Result    : {result}\n")
            else:
                if Game.player_symbol == Board.max_symbol:
                    f.write(f"Players   : Player - Computer\n")
                else:
                    f.write(f"Players   : Computer - Player\n")
                f.write(f"Result    : {result}\n")
                f.write(f"Algorithm : {Game.algorithm}\n")
                f.write(f"Difficulty: {Game.difficulty}\n")

            f.write(f"Board size: {Board.no_lines}x{Board.no_columns}\n")
            f.write(f"Duration  : {time:.2f} seconds\n")

    # Prints the final score and the winner, also waits for input to continue
    # For the GUI, that input means quitting the window
    # For the CLI, that input means pressing any key to continue
    @staticmethod
    def print_result(time, boxes=[]):
        input_handler.clear_screen()

        board = Game.game_board

        print(Game.get_instance(), end="\n\n")
        Game.print_score()

        # print the winner
        if board.max_score == board.min_score:
            print("It's a tie!")
            Game.write_result("1/2 - 1/2", time)
        else:
            if Game.pvp:
                print("Player " + (f"{Board.max_symbol}" if board.max_score > board.min_score else f"{Board.min_symbol}") + " won!", time)
                Game.write_result("1 - 0" if board.max_score > board.min_score else "0 - 1", time)
            else:
                player_score   = board.max_score if Game.player_symbol == Board.max_symbol else board.min_score
                computer_score = board.min_score if Game.player_symbol == Board.max_symbol else board.max_score

                print(("Player " if player_score > computer_score else "Computer ") + "won!")
                if Game.player_symbol == Board.max_symbol:
                    Game.write_result("1 - 0" if player_score > computer_score else "0 - 1", time)
                else:
                    Game.write_result("0 - 1" if player_score > computer_score else "1 - 0", time)

        print(f"\nTime: {time:.2f} seconds")

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
        game                = Game.get_instance()
        board               = Game.game_board
        computer_move_count = (1 if Game.player_symbol == Board.min_symbol else 2)

        if Game.gui:
            boxes = Graphics().start_graphics(game)

        time_start = time.time()
        while not board.is_finished():
            input_handler.clear_screen()

            print(Game.get_instance())

            Game.print_current_player()

            if not Game.pvp and board.current_player != Game.player_symbol:
                computer_move_count = Game.computer_move(computer_move_count)

                if Game.gui:
                    boxes = Graphics().display_game_board(game)
            else:
                if Game.gui:
                    boxes = Game.get_gui_move_from_user(boxes)
                else:
                    Game.get_coordinates_from_user()

            if not board.completed_box:
                board.current_player = board.get_opponent()

        if Game.gui:
            Game.print_result(time.time() - time_start, boxes)
        else:
            Game.print_result(time.time() - time_start)

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
                Alpha_Beta.difficulty = str(Game.difficulty)
                Ida_Star.difficulty = str(Game.difficulty)
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

    # Toggles the game mode
    @staticmethod
    def toggle_gamemode():
        Game.pvp = not Game.pvp

    # Changes the starting player
    @staticmethod
    def switch_starting_player():
        Ida_Star.computer_symbol = Game.player_symbol
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

    # Writes the match number in the logs
    @staticmethod
    def write_match_number(file_name):
        with open(path.join(Game.log_dir, f"{file_name}.txt"), 'w' if Game.match_number == 1 else 'a') as f:
            if Game.match_number != 1:
                f.write("\n")
            f.write("Match " + str(Game.match_number) + '\n')

    # Prints the logs to the screen
    @staticmethod
    def write_file(file_name):
        input_handler.clear_screen()

        if Game.match_number != 1:
            with open(path.join(Game.log_dir, f"{file_name}.txt"), 'r') as f:
                print(f.read())
            try:
                _ = input("\nPress any key to continue...")
            except KeyboardInterrupt:
                Game.quit()
        else:
            print("No matches played yet")
            try:
                _ = input("\nPress any key to continue...")
            except KeyboardInterrupt:
                Game.quit()

    # The main menu for the PvP game mode
    @staticmethod
    def main_menu_pvp():
        options = "Start game, " + \
                  "See match history, " + \
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
                    Game.write_match_number("time")
                    with open(path.join(Game.log_dir, 'time.txt'), 'a') as f:
                        f.write("Player - Player\n")

                    Game.write_match_number("match_history")
                    Game.match_number += 1
                    
                    Game.play()
                elif option == '2':
                    Game.write_file("match_history")
                elif option == '3':
                    Game.change_game_board_sizes()
                elif option == '4':
                    Game.toggle_gamemode()
                elif option == '5':
                    Game.toggle_gui()

                Game.main_menu()
        except KeyboardInterrupt:
            Game.quit()

    # The main menu for the PvE game mode
    @staticmethod
    def main_menu_pve():
        options = "Start game, " + \
                  "See match history, " + \
                  "Change the board sizes (" + str(Board.no_lines) + "x" + str(Board.no_columns) + "), " + \
                  "Choose the game type (Pv" + ("P" if Game.pvp else "E") + "), " + \
                  "Toggle GUI (" + ("On" if Game.gui else "Off") + "), " + \
                  "Change the computer's algorithm (" + str(Game.algorithm) + "), " + \
                  "Change difficulty (" + str(Game.difficulty) + "), " + \
                  "Change who starts first (" + ("Player" if Game.player_symbol == Board.max_symbol else "Computer") + "), " + \
                  "See computer time logs, " + \
                  "Quit"

        try:
            option = input_handler.get_valid_input(Game.logo() + "\n\n< Choose an option >", options)

            if option == '0':
                Game.quit(True)
            else:
                if option == '1':
                    Game.write_match_number("time")
                    Game.write_match_number("match_history")
                    Game.match_number += 1

                    Game.play()
                elif option == '2':
                    Game.write_file("match_history")
                elif option == '3':
                    Game.change_game_board_sizes()
                elif option == '4':
                    Game.toggle_gamemode()
                elif option == '5':
                    Game.toggle_gui()
                elif option == '6':
                    Game.change_algorithm()
                elif option == '7':
                    Game.change_difficulty()
                elif option == '8':
                    Game.switch_starting_player()
                elif option == '9':
                    Game.write_file("time")

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
