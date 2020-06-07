class Error(Exception):
    """Base error"""
    pass


class GameNotFoundError(Error):
    """Raised when the game ID cannor be found"""

    def __init__(self, message="\n[ERROR] Could not find any game with the selected ID"):
        self.message = message
        print(message)


class InputError(Error):
    """Raised when the input is not valid"""

    def __init__(self, message="\n[ERROR] Please enter a valid GameID or type `exit` to quit"):
        self.message = message
        print(message)
