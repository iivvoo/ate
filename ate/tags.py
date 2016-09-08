import re

from .exceptions import ParseError
from .registry import Registry


class Node:

    def __init__(self, parent=None):
        self.code = ""
        self.parent = parent

    def render(self, context):
        return self.code

    def __str__(self):
        return "Plain node ----\n{}\n----\n".format(self.code)


class TextNode(Node):

    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.text = text

    def render(self, context):
        return self.text

    def __str__(self):
        return "Text node ----\n{}\n----\n".format(self.text)


class ExpressionNode(Node):

    def __init__(self, expression, parent=None):
        super().__init__(parent=parent)
        # should {{ }} be removed from expression already?
        self.expression = expression

    def render(self, context):
        expr = self.expression[2:-2]  # remove {{ }}
        return str(context.eval(expr))

    def __str__(self):
        return "Statement node ----\n{}\n----\n".format(self.expression)


class StatementNode(Node):
    open = ''

    def __init__(self, type, expression="", parent=None):
        super().__init__(parent=parent)
        self.type = type
        self.expression = expression

    def compile(self, code, index=0):
        return index


class BlockStatementNode(StatementNode):
    closing = None
    has_block = True

    def __init__(self, type, expression="", nodes=None, parent=None):
        super().__init__(type, expression, parent=parent)
        self.nodes = nodes or []

    def render(self, context):
        # The blockstatement itself will probably render to nothing
        # so just include the childnodes
        res = []
        for node in self.nodes:
            res.append(node.render(context))
        return res

    def __str__(self):
        return "BlockStatement node {}----\n{}\n----\n".format(
            self.type, self.code)

    def __iter__(self):
        return self.nodes

    def compile(self, code, index=0):
        """ Wrap nodes in MainNode or something? """
        res = []
        closing = self.closing
        closing_found = closing is None

        while index < len(code):
            first_marker = code[index:].find('{')
            if first_marker == -1:
                res.append(TextNode(code[index:]))
                index = len(code)
                break

            if first_marker > 0:
                # Is there any text to put in a node?
                res.append(TextNode(code[index:index + first_marker]))
                index += first_marker

            if closing and re.match("{{%\s*{}\s*%}}".format(closing),
                                    code[index:]):
                closing_found = True
                index += code[index:].find("%}") + 2
                break

            node, skip = CompileStatement(code[index:], parent=self)
            res.append(node)
            index += skip

        if not closing_found:
            raise ParseError("Closing tag {} not found".format(closing))

        self.nodes = res
        self.code = code[:index]
        return index


class MainNode(BlockStatementNode):
    pass


class ForBlockStatementNode(BlockStatementNode):
    open = 'for'
    closing = 'endfor'

    def render(self, context):
        var, _in, expr = self.expression.partition(" in ")
        var = var.strip()
        seq = context.eval(expr.strip())

        res = []
        for element in seq:
            context.push({var: element})
            for node in self.nodes:
                res.append(node.render(context))
            context.pop()

        return res


class IfBlockStatementNode(BlockStatementNode):
    open = 'if'
    closing = 'endif'

    def render(self, context):
        res = []
        t, f = [], []

        current = t
        for node in self.nodes:
            if isinstance(node, ElseInIfStatementNode):
                current = f
            else:
                current.append(node)

        if context.eval(self.expression):
            for node in t:
                res.append(node.render(context))
        else:
            for node in f:
                res.append(node.render(context))
        return res


class ElseInIfStatementNode(StatementNode):
    """ Should only be allowed inside if blockstatement """
    open = 'else'


registry = Registry()

registry.register('for', ForBlockStatementNode, MainNode)
registry.register('if', IfBlockStatementNode, MainNode)
registry.register('else', ElseInIfStatementNode, IfBlockStatementNode, direct=True)
# registry.register('else', ForBlockStatementNode, direct=True)


def CompileStatement(code, parent=None):
    parent = parent or MainNode("main")
    end = code.find("}")
    if end == -1:
        raise ParseError("Closing } missing")
    if code[1] == '{':  # non-block statement
        # assume } follows closing } -> +2
        return ExpressionNode(code[:end + 2]), end + 2

    # assume it's {%. Adjust end to compensate for
    # closing %
    statement = code[2:end - 1].strip()
    main, _, expr = statement.partition(" ")

    klass = registry.find(main, parent)

    node = klass(main, expr, parent=parent)
    end = node.compile(code, end + 1)

    # No node is inserted, it purely returns body
    return node, end
