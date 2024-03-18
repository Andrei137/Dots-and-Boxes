from os import system, name
from time import sleep


# Clears the screen
def clear_screen():
    # Windows
    if name == "nt":
        system("cls")
    # Unix
    else:
        system("clear")


# Handles the input of the user
# Will reset the current screen in case of invalid input
def get_valid_input(title, text="", board_menu=False):

    # Formats a string into options
    def turn_into_options(text):
        '''
            For example, the text "Start, Settings, Quit" becomes
            [1] Start
            [2] Settings
            [0] Quit

            ->
        '''
        text = text.split(", ")
        options = ''

        for i, word in enumerate(text):
            if word == "Quit" or word == "Back":
                options += f"[0] {word}"
            else:
                options += f"[{i + 1}] {word}\n"

        return options + "\n\n-> "

    if board_menu:
        options = "[?] Select any number from 3 to 8\n[0] Go back\n\n-> "
        viable_options = [str(i) for i in range(3, 9)] + ['0']
    else:
        options = turn_into_options(text)
        viable_options = [s[0] for s in options.split('[') if len(s) > 1 and s[0].isdigit()]

    while True:
        clear_screen()
        print(title)
        try:
            option = input(options)

            if option in viable_options:
                return option
            print(f"Invalid input. Please type again")
            sleep(1.25)
        except (KeyboardInterrupt, EOFError):
            clear_screen()
            exit(0)
