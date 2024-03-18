from enum import Enum


class Algorithm(Enum):
    IDA_STAR         = 1
    ALPHA_BETA       = 2
    BAYESIAN_NETWORK = 3

    def __str__(self):
        # IDA* looks better with the * symbol
        if self == Algorithm.IDA_STAR:
            return "IDA*"
        return self.name.replace('_', ' ').title()

    # Returns the chosen algorithm
    @staticmethod
    def select_algorithm(option):
        if option == '1':
            return Algorithm.IDA_STAR
        elif option == '2':
            return Algorithm.ALPHA_BETA
        elif option == '3':
            return Algorithm.BAYESIAN_NETWORK
        else:
            return None


class Difficulty(Enum):
    EASY   = 1
    MEDIUM = 2
    HARD   = 3

    def __str__(self):
        return self.name.title()

    # Returns the chosen algorithm
    @staticmethod
    def select_difficulty(option):
        if option == '1':
            return Difficulty.EASY
        elif option == '2':
            return Difficulty.MEDIUM
        elif option == '3':
            return Difficulty.HARD
        else:
            return None
