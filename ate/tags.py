import re
from collections import namedtuple

from .exceptions import ParseError, ExpressionNotClosed
from .exceptions import NotClosedError, StatementNotFound
from .exceptions import StatementNotAllowed, UnexpectedClosingFound
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
        self.expression = expression

    def render(self, context):
        return str(context.eval(self.expression))

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


class CommentNode(StatementNode):

    def __init__(self, expression="", parent=None):
        super().__init__("comment", expression=expression, parent=parent)


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

    def find_start_block(self, code):
        """ find the start of the nearest block: {{ {% or {# """
        indexes = []

        for start in ('{%', '{{', '{#'):
            index = code.find(start)
            if index != -1:
                indexes.append(index)

        if indexes:
            return min(indexes)
        return -1

    def compile(self, pc, index=0):
        res = []
        code = pc.code
        closing = self.closing
        closing_found = closing is None

        while index < len(code):
            first_marker = self.find_start_block(code[index:])

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

            node, skip = CompileStatement(pc[index:], parent=self)
            res.append(node)
            index += skip

        if not closing_found:
            raise ParseError("Closing tag {} not found".format(closing),
                             pc)

        self.nodes = res
        self.code = code[:index]
        return index


class MainNode(BlockStatementNode):
    pass


class FillBlockStatementNode(BlockStatementNode):
    open = 'fill'
    closing = 'endfill'


class ForBlockStatementNode(BlockStatementNode):
    open = 'for'
    closing = 'endfor'

    def looper(self, sequence):
        looptype = namedtuple("Loop", ["index", "index0", "first", "last"])
        l = len(sequence)

        for i, v in enumerate(sequence):
            yield looptype(i, i + 1, i == 0, i == l - 1), v

    def render(self, context):
        var, _in, expr = self.expression.partition(" in ")
        var = var.strip()
        seq = context.eval(expr.strip())

        res = []
        for loop, element in self.looper(seq):
            context.push({var: element, 'loop': loop})
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


class SlotStatementNode(BlockStatementNode):
    open = 'slot'
    closing = 'endslot'

    def render(self, context):
        res = []

        blockname = self.expression or "main"
        block_found = False
        # is there a child to pop? E.g. rendering base template directly
        if context.child():
            with context.popchild() as tpl:
                for node in tpl.mainnode.nodes:
                    if isinstance(node, FillBlockStatementNode):
                        block_found = True
                        if node.expression == blockname:
                            res.append(node.render(context))
                            break
                else:
                    if not block_found:
                        # use entire template as matching block
                        block_found = True
                        res.append(tpl.render_with_context(
                            context,
                            start_at_parent=False))
                    else:
                        # render the body of the block
                        for node in self.nodes:
                            res.append(node.render(context))
        else:
            # render the body of the block
            for node in self.nodes:
                res.append(node.render(context))
        return res


registry = Registry()

registry.register('for', ForBlockStatementNode, MainNode)
registry.register('if', IfBlockStatementNode, MainNode)
registry.register('else', ElseInIfStatementNode,
                  IfBlockStatementNode, direct=True)
# registry.register('else', ForBlockStatementNode, direct=True)
registry.register('slot', SlotStatementNode, MainNode)
registry.register('fill', FillBlockStatementNode, MainNode)


def parse_expression(code, start="{{", end="}}"):
    """ parse any expression surrounded by start/end,
        supporting string expressions containing start/end
        markers. Code may contain trailing code

        return index where parsing ends including parsing of endmarker
    """
    assert code[:2] == start

    escape_mode = False
    string_mode = ''  # can be ' " or empty
    res = ''

    for index in range(2, len(code)):
        c = code[index]

        if string_mode:
            if not escape_mode:
                if c == string_mode:
                    string_mode = False
                if c == '\\':
                    escape_mode = True
            else:
                escape_mode = False

        elif c in "'\"":
            string_mode = c

        elif code[index:index + 2] == end:
            # 'end' ends the expression and we're not inside a string
            index += 1  # we read one } ahead (assume end is 2 characters)
            break
        res += c
    else:
        raise ExpressionNotClosed()
    return res, index + 1


def parse_statement(code):
    """ parse
        {% stmnt expr %}
        where "expr" may contain a string containing '%}'
    """
    r = parse_expression(code, start='{%', end='%}')
    return r


def parse_comment(code):
    r = parse_expression(code, start='{#', end='#}')
    return r


def CompileStatement(pc, parent=None):
    """ Either a block statement {% or expression statement {{
        has started. Figure out what it is and parse it
    """
    parent = parent or MainNode("main")

    # we have a parse context. catch errors and add line numbers etc?
    if pc.code[1] == '{':  # expression statement
        try:
            expr, end = parse_expression(pc.code)
        except ExpressionNotClosed as e:
            raise ParseError("Expression not closed", pc) from e
        return ExpressionNode(expr), end

    if pc.code[1] == '#':  # comment
        try:
            expr, end = parse_comment(pc.code)
        except ExpressionNotClosed as e:
            raise ParseError("Comment not closed", pc) from e
        return CommentNode(expr), end

    try:
        statement, end = parse_statement(pc.code)
    except ExpressionNotClosed as e:
        raise ParseError("Statement not closed", pc) from e
    statement = statement.strip()

    main, _, expr = statement.partition(" ")

    pc.tag = main
    try:
        klass = registry.find(main, parent)
    except NotClosedError as e:
        raise ParseError("Statement not closed", pc) from e
    except StatementNotFound as e:
        raise ParseError("Statement not found", pc) from e
    except StatementNotAllowed as e:
        raise ParseError("Statement not allowed", pc) from e
    except UnexpectedClosingFound as e:
        raise ParseError("Unexpected closing statement found", pc) from e

    node = klass(main, expr, parent=parent)
    pc.node = node

    end = node.compile(pc, end)

    # No node is inserted, it purely returns body
    return node, end
