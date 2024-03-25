from os import environ, path
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # disable Hello message from pygame
import pygame
import sys
import src.game_logic.game


class Graphics:
    # Singleton class
    instance = None

    # Pygame screen
    screen = None

    # Constants
    box_length = 75
    scale = 2
    grey = (128, 128, 128)

    # Resource directory path
    if getattr(sys, 'frozen', False):  # if the application is bundled by PyInstaller
        resource_dir = path.join(sys._MEIPASS, 'resources')
    else:
        resource_dir = path.join(path.dirname(__file__), '..', '..', 'resources')

    # Images
    line_image = pygame.image.load(path.join(resource_dir, 'Line.png'))
    dot_image = pygame.image.load(path.join(resource_dir, 'Dot.png'))
    x_image = pygame.image.load(path.join(resource_dir, 'X.png'))
    o_image = pygame.image.load(path.join(resource_dir, 'O.png'))

    # Singleton class
    @classmethod
    def get_instance(cls, game):
        if cls.instance is None:
            cls.instance = cls.__new__(cls)
            board = game.game_board

            # make the dimensions of the screen dynamic
            cls.screen_width = (Graphics.scale * board.no_columns - 1) * Graphics.box_length
            cls.screen_height = (Graphics.scale * board.no_lines - 1) * Graphics.box_length

            # the images are scaled to fit the boxes
            size = (Graphics.box_length, Graphics.box_length)
            cls.horizontal_line = pygame.transform.scale(Graphics.line_image, size)
            cls.vertical_line = pygame.transform.rotate(Graphics.horizontal_line, 90)
            cls.dot = pygame.transform.scale(Graphics.dot_image, size)
            cls.x = pygame.transform.scale(Graphics.x_image, size)
            cls.o = pygame.transform.scale(Graphics.o_image, size)
        return cls.instance

    # In case the game board dimensions got modified, update the screen dimensions
    @classmethod
    def update_width_height(cls, game):
        board = game.game_board

        cls.screen_width = (Graphics.scale * board.no_columns - 1) * Graphics.box_length
        cls.screen_height = (Graphics.scale * board.no_lines - 1) * Graphics.box_length

    # Displays the box at the given position
    @staticmethod
    def display_box(game, line, column):
        # assert types
        assert isinstance(line, int), "Wrong parameter type"
        assert isinstance(column, int), "Wrong parameter type"

        graphics = Graphics.get_instance(game)
        board = game.game_board
        size = (column * Graphics.box_length, line * Graphics.box_length)

        if not (line & 1):
            if not (column & 1):
                # both coordinates are even -> dot
                Graphics.screen.blit(graphics.dot, size)
            else:
                # odd column and even line -> horizontal line (if it exists)
                if line != Graphics.scale * board.no_lines and \
                   board.boxes[line // Graphics.scale][column // Graphics.scale].up:
                    Graphics.screen.blit(graphics.horizontal_line, size)

                # special case for the last line
                if line == Graphics.scale * board.no_lines and \
                   board.boxes[line // Graphics.scale - 1][column // Graphics.scale].down:
                    Graphics.screen.blit(graphics.horizontal_line, size)
        elif not (column & 1):
            # even column and odd line -> vertical line (if it exists)
            if column != Graphics.scale * board.no_columns and \
               board.boxes[line // Graphics.scale][column // Graphics.scale].left:
                Graphics.screen.blit(graphics.vertical_line, size)

            # special case for the last column
            if column == Graphics.scale * board.no_columns and \
               board.boxes[line // Graphics.scale][column // Graphics.scale - 1].right:
                Graphics.screen.blit(graphics.vertical_line, size)
        # both coordinates are odd -> symbol
        elif line & 1 == column & 1 == 1:
            # check if the symbol is X or O to display it
            if board.boxes[line // Graphics.scale][column // Graphics.scale].symbol == 'X':
                Graphics.screen.blit(graphics.x, size)
            elif board.boxes[line // Graphics.scale][column // Graphics.scale].symbol == 'O':
                Graphics.screen.blit(graphics.o, size)

    # Displays the current game board and return the current boxes
    @staticmethod
    def display_game_board(game):
        # make the screen grey
        Graphics.screen.fill(Graphics.grey)

        boxes = []
        board = game.game_board

        for line in range(Graphics.scale * board.no_lines + 1):
            box_line = []

            for column in range(Graphics.scale * board.no_columns + 1):
                # create a box
                area = pygame.Rect(column * (Graphics.box_length), line * (Graphics.box_length),
                                   Graphics.box_length, Graphics.box_length)
                # draw the box
                pygame.draw.rect(Graphics.screen, Graphics.grey, area)
                # draw the box content
                Graphics.display_box(game, line, column)
                # add the box to the list
                box_line.append(area)

            # add the line of boxes to the list
            boxes.append(box_line)

        # update the screen
        pygame.display.flip()
        return boxes

    # Gets the coordinates of the line that was clicked by the user
    @staticmethod
    def player_click(game, boxes, finished=False):
        # assert types
        assert isinstance(finished, bool), "Wrong parameter type"

        board = game.game_board

        while True:
            try:
                for current_event in pygame.event.get():
                    # if the user closes the window, quit the game
                    if current_event.type == pygame.QUIT:
                        return None, None
                    # if the user clicks the mouse, check if the click was on a line
                    elif current_event.type == pygame.MOUSEBUTTONDOWN and not finished:
                        position = pygame.mouse.get_pos()

                        for line in range(Graphics.scale * board.no_lines - 1):
                            for column in range(Graphics.scale * board.no_columns - 1):
                                # the click is on a line if it the coordinates have different parity
                                if boxes[line][column].collidepoint(position) and \
                                   line % Graphics.scale != column % Graphics.scale:
                                    return line, column
            except KeyboardInterrupt:
                return None, None

    # Starts the graphics interface
    @staticmethod
    def start_graphics(game):
        pygame.init()
        pygame.display.set_caption('Dots and Boxes')

        graphics = Graphics.get_instance(game)
        Graphics.screen = pygame.display.set_mode((graphics.screen_width, graphics.screen_height))

        return Graphics.display_game_board(game)

    # Quits the graphics interface
    @staticmethod
    def quit_graphics():
        pygame.quit()
