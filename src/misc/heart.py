# Credit - https://github.com/liuyubobobo/heart-curve-cplusplus
# Translated from C++ to Python by me
# The message and the color red are also added by me
# I don't know enough math to explain how this works :3


import math
from os import name
from colorama import Fore, init


class Heart:
    instance = None  # Singleton class
    message  = ["THANK", "  U FOR  ", "PLAYING"]

    # Singleton class
    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
            if name == "nt":
                init(convert=True)
        return cls.instance

    @staticmethod
    def fast_check(x, value1, value2, sign):
        if sign == '|':
            return x <= value1 or x >= value2
        else:
            return x > value1 and x < value2

    @staticmethod
    def is_inside_heart(x, y):
        return x * x + math.pow(5.0 * y / 4.0 - math.sqrt(abs(x)), 2) - 1 <= 0.0

    @staticmethod
    def print_heart(x, y, condition):

        # make the heart red
        print(f"{Fore.RED}", end='')

        if Heart.is_inside_heart(x, y) and condition:
            print('*', end='')
        else:
            print(' ', end='')

    @staticmethod
    def print_message(x, y, condition, i, j):
        if Heart.is_inside_heart(x, y):
            if Heart.fast_check(x, -0.33, 0.33, '|'):
                # red
                print(f"{Fore.RED}*", end='')
            elif condition:
                # blank space
                print(f' ', end='')
            else:
                # default
                print(f"{Fore.RESET}" + Heart.message[i][j], end='')
                return 1  # increment j
        else:
            print(' ', end='')

        # don't increment j
        return 0

    @staticmethod
    def for_heart(y, condition):
        i = -1.1

        while i <= 1.1:
            if condition == 1:
                Heart.print_heart(i, y, Heart.fast_check(i, -0.33, 0.33, '|'))
            else:
                Heart.print_heart(i, y, True)

            i += 0.025

    @staticmethod
    def for_message(y, condition):
        k = [0, 0, 0]
        i = -1.1

        while i < 1.1:
            if condition == 1:
                if Heart.print_message(i, y, Heart.fast_check(i, -0.06, 0.06, '|'), 0, k[0]):
                    k[0] += 1
            elif condition == 2:
                if Heart.print_message(i, y, Heart.fast_check(i, -0.12, 0.12, '|'), 1, k[1]):
                    k[1] += 1
            else:
                if Heart.print_message(i, y, Heart.fast_check(i, -0.08, 0.08, '|'), 2, k[2]):
                    k[2] += 1

            i += 0.025

    @staticmethod
    def print_full_heart():

        # compatibility with Windows
        if name == "nt":
            init(convert=True)

        y = 1.3

        while y >= -0.7:
            if Heart.fast_check(y, 0.5, 0.55, '&'):
                Heart.for_message(y, 1)
            elif Heart.fast_check(y, 0.39, 0.45, '&'):
                Heart.for_message(y, 2)
            elif Heart.fast_check(y, 0.25, 0.3, '&'):
                Heart.for_message(y, 3)
            elif Heart.fast_check(y, 0.2, 0.6, '&'):
                Heart.for_heart(y, 1)
            else:
                Heart.for_heart(y, 2)
            print()
            y -= 0.06

        # reset the color
        print(f"{Fore.RESET}\n")
