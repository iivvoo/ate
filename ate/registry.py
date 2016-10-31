from .exceptions import StatementNotAllowed
from .exceptions import StatementNotFound, UnexpectedClosingFound


class Registry:

    def __init__(self):
        self._reg = []

    def register(self, tagname, tagclass, parent, direct=False):
        self._reg.append((tagname, tagclass, parent, direct))

    def find(self, tag, node):
        any_found = False
        is_closing = False

        for tagname, nodeclass, parent, direct in self._reg:
            if tagname == tag:
                any_found = True
                if node.__class__ == parent:
                    return nodeclass
                if direct:
                    continue  # must be direct, don't look further
                n = node
                while n.parent:
                    if n.parent.__class__ == parent:
                        return nodeclass
                    n = n.parent

            # we're not meant to handle closing tags but detecting it
            # allows for easier error reports
            try:
                if tag == nodeclass.closing:
                    is_closing = True
            except AttributeError:
                # only block statements have a closing tag
                pass
        if any_found:
            # the tag exists but is not allowed in a specific context
            raise StatementNotAllowed(tag)
        # did we run into a closing statement? In other words,
        # opening statement was missing or not parsable
        if is_closing:
            raise UnexpectedClosingFound(tag)
        raise StatementNotFound(tag)
