from .exceptions import StatementNotAllowed
from .exceptions import StatementNotFound


class Registry:

    def __init__(self):
        self._reg = []

    def register(self, tagname, tagclass, parent, direct=False):
        self._reg.append((tagname, tagclass, parent, direct))

    def find(self, tag, node):
        any_found = False

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

        if any_found:
            # the tag exists but is not allowed in a specific context
            raise StatementNotAllowed(tag)
        raise StatementNotFound(tag)

