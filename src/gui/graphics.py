from time import sleep
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # disable Hello message from pygame 
import pygame


class Graphics:
    instance = None  # Singleton class

    screen = None  # Pygame screen

    # Constants
    box_length = 75
    scale      = 2
    grey       = (128, 128, 128)

    # Images
    line_image = pygame.image.load("resources\\Line.png")
    dot_image  = pygame.image.load("resources\\Dot.png")
    x_image    = pygame.image.load("resources\\X.png")
    o_image    = pygame.image.load("resources\\O.png")

    # Singleton class
    @classmethod
    def get_instance(cls, game):
        if cls.instance is None:
            cls.instance = cls.__new__(cls)

            # make the dimensions of the screen dynamic
            cls.screen_width  = (Graphics.scale * game.game_board.no_columns - 1) * Graphics.box_length
            cls.screen_height = (Graphics.scale * game.game_board.no_lines - 1) * Graphics.box_length

            # the images are scaled to fit the boxes
            cls.horizontal_line = pygame.transform.scale(Graphics.line_image, (Graphics.box_length, Graphics.box_length))
            cls.vertical_line   = pygame.transform.rotate(Graphics.horizontal_line, 90)
            cls.dot             = pygame.transform.scale(Graphics.dot_image, (Graphics.box_length, Graphics.box_length))
            cls.x               = pygame.transform.scale(Graphics.x_image, (Graphics.box_length, Graphics.box_length))
            cls.o               = pygame.transform.scale(Graphics.o_image, (Graphics.box_length, Graphics.box_length))
        return cls.instance

    # In case we modify the game board dimensions, we need to update the screen dimensions
    @classmethod
    def update_width_height(cls, game):
        cls.screen_width  = (Graphics.scale * game.game_board.no_columns - 1) * Graphics.box_length
        cls.screen_height = (Graphics.scale * game.game_board.no_lines - 1) * Graphics.box_length

    # Displays the box at the given position
    @staticmethod
    def display_box(game, line, column):
        graphics = Graphics.get_instance(game)

        if not (line & 1):
            if not (column & 1):
                # if both coordinates are even, we have a dot
                Graphics.screen.blit(graphics.dot, (column * Graphics.box_length, line * Graphics.box_length))
            else:
                # if we have an odd column and an even line, we have a horizontal line (if it exists)
                if line != Graphics.scale * game.game_board.no_lines and game.game_board.boxes[line // Graphics.scale][column // Graphics.scale].up:
                    Graphics.screen.blit(graphics.horizontal_line, (column * Graphics.box_length, line * Graphics.box_length))

                # special case for the last line
                if line == Graphics.scale * game.game_board.no_lines and game.game_board.boxes[line // Graphics.scale - 1][column // Graphics.scale].down:
                    Graphics.screen.blit(graphics.horizontal_line, (column * Graphics.box_length, line * Graphics.box_length))
        elif not (column & 1):
            # if we have an even column and an odd line, we have a vertical line (if it exists)
            if column != Graphics.scale * game.game_board.no_columns and game.game_board.boxes[line // Graphics.scale][column // Graphics.scale].left:
                Graphics.screen.blit(graphics.vertical_line, (column * Graphics.box_length, line * Graphics.box_length))

            # special case for the last column
            if column == Graphics.scale * game.game_board.no_columns and game.game_board.boxes[line // Graphics.scale][column // Graphics.scale - 1].right:
                Graphics.screen.blit(graphics.vertical_line, (column * Graphics.box_length, line * Graphics.box_length))
        # if both coordinates are odd, we might have a symbol
        elif line & 1 == column & 1 == 1:
            # check if we have X or O
            if game.game_board.boxes[line // Graphics.scale][column // Graphics.scale].symbol == 'X':
                Graphics.screen.blit(graphics.x, (column * Graphics.box_length, line * Graphics.box_length))
            elif game.game_board.boxes[line // Graphics.scale][column // Graphics.scale].symbol == 'O':
                Graphics.screen.blit(graphics.o, (column * Graphics.box_length, line * Graphics.box_length))

    # Displays the current game board and return the current boxes
    @staticmethod
    def display_game_board(game):
        # make the screen grey
        Graphics.screen.fill(Graphics.grey)
        boxes = []

        for line in range(Graphics.scale * game.game_board.no_lines + 1):
            box_line = []

            for column in range(Graphics.scale * game.game_board.no_columns + 1):
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
        running = True
        while running:
            try:
                for current_event in pygame.event.get():
                    # if the user closes the window, we quit the game
                    if current_event.type == pygame.QUIT:
                        running = False
                    # if the user clicks the mouse, we check if the click was on a line
                    elif current_event.type == pygame.MOUSEBUTTONDOWN and not finished:
                        position = pygame.mouse.get_pos()

                        for line in range(Graphics.scale * game.game_board.no_lines - 1):
                            for column in range(Graphics.scale * game.game_board.no_columns - 1):
                                # the click is on a line if it the coordinates have different parity
                                if boxes[line][column].collidepoint(position) and line % Graphics.scale != column % Graphics.scale:
                                    return line, column
            except KeyboardInterrupt:
                running = False
        if not running:
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