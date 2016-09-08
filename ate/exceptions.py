class ATEException(Exception):
    pass


class ParseError(ATEException):
    pass


class StatementNotFound(ATEException):
    pass


class StatementNotAllowed(ATEException):
    pass

