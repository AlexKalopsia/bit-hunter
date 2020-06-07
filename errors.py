class Error(Exception):
    """Base error"""
    pass


class GameNotFoundError(Error):
    """Raised when the game ID cannor be found

    Attributes:
        gameID -- input game ID which caused the error
        message -- explanation of the error
    """

    def __init__(self, _gameID):
        self.gameID = _gameID
        self.message = "[ERROR] Could not find any game with ID " + \
            str(self.gameID)
        print(self.message)


class InputError(Error):
    """Raised when the input is not valid"""

    def __init__(self):
        self.message = "\n[ERROR] Please enter a numeric GameID or type `exit` to quit"
        print(self.message)
