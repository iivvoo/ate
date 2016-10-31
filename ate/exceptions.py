class ATEException(Exception):
    pass


class ExpressionNotClosed(ATEException):
    pass


class ParseError(ATEException):

    def __init__(self, message, pc):
        super().__init__(message)
        self.pc = pc


class NotClosedError(ParseError):
    pass


class StatementNotFound(ATEException):
    pass


class StatementNotAllowed(ATEException):
    pass


class UnexpectedClosingFound(ATEException):
    pass
