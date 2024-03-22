from game_logic import game


def main():
    game_instance = game.Game().get_instance()
    game_instance.main_menu()

if __name__ == "__main__":
    main()
