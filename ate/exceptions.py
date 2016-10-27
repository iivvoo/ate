class ATEException(Exception):
    pass


class ParseError(ATEException):

    def __init__(self, message, code=""):
        super().__init__(message)
        self.code = code


class NotClosedError(ParseError):
    pass


class StatementNotFound(ATEException):
    pass


class StatementNotAllowed(ATEException):
    pass
