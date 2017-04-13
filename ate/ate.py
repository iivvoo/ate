"""

nomenclature (taken from jinja2):
{{ }} expression
{% something %} statement. May not always have a block
 (e.g. extends, include)
 may have specific sub statements

There are two constructs:

Simple statements, {{ expr }} and blockstatements
{%if expr %} .. {%endif%}

But what's {%else%} in such a construct? It can be considered
a "blockless blockstatement" (so no "endelse")

{%else%} does not exist outside an if statement. It may exist
in for example a for statement


TODO:

- sensible errors, line numbers
- rename

"""
import simpleeval
from contextlib import contextmanager

from .tags import MainNode


class Context:
    """
        Make it a context manager so context get popped automatically?

        with context.add({'a':1}):
            ....

    """
    evaluator_class = simpleeval.SimpleEval
    functions = {}

    def __init__(self, data={}):
        self.stack = [data]
        self.children = []
        self.evaluator = self.evaluator_class(names=self.name_handler, functions=self.functions)

    def name_handler(self, node):
        name = node.id
        for ctx in reversed(self.stack):
            try:
                return ctx[name]
            except KeyError:
                pass

        raise NameError(name)

    def child(self):
        if self.children:
            return self.children[-1]
        return None

    def pushchild(self, child):
        self.children.append(child)

    @contextmanager
    def popchild(self):
        c = self.children.pop()
        yield c
        self.children.append(c)

    @contextmanager
    def __call__(self, data={}):
        self.push(data)
        yield
        self.pop()

    def push(self, data={}):
        self.stack.append(data)

    def pop(self):
        self.stack.pop()

    def eval(self, expr):
        try:
            return self.evaluator.eval(expr.lstrip())
        except simpleeval.AttributeDoesNotExist as e:
            return "??{}??".format(e.expression)


def flatten(l):
    """ flatten recursive, nested lists of strings """
    # StringIO might be more efficient?
    b = ""
    for i in l:
        if isinstance(l, list):
            b += flatten(i)
        else:
            b += i
    return b


class ParseContext:
    """
        ParseContext is used to keep track of where we currently are in a
        template. Mostly for (more) detailed error reporting.

        http://stackoverflow.com/questions/5722006/does-python-do-slice-by-reference-on-strings
    """

    def __init__(self, code, offset=0, parent=None):
        self.code = code
        self.offset = offset
        self.parent = parent
        self.node = None
        self.tag = ""

    def __len__(self):
        return len(self.code) - self.offset

    def __getitem__(self, i):
        if isinstance(i, slice):
            offset = i.start or 0
            return ParseContext(self.code[i], offset=self.offset + offset,
                                parent=self)
        return self.code[i]

    def position(self):
        offset = self.offset
        p = self
        while True:
            # offset += p.offset
            code = p.code
            if not p.parent:
                break
            p = p.parent

        line = code[:offset].count('\n') + 1  # 1-based
        col = len(code[:offset].rsplit("\n", 1)[-1]) + 1  # 1-based
        return line, col


class Template:
    context_class = Context

    def __init__(self, code, parent=None, context_class=None):
        self.code = code
        self.mainnode = self.compile()
        self.rendered = []
        self.parent = parent
        self.context_class = context_class or self.context_class

    def compile(self):
        node = MainNode(type="main")
        node.compile(ParseContext(self.code))
        return node

    def render_with_context(self, context, start_at_parent=True):
        with context({}):
            if self.parent and start_at_parent:
                context.pushchild(self)
                return self.parent.render_with_context(context)

            return self.mainnode.render(context)

    def render_nested(self, *, context=None, context_class=None, **data):
        if not context:
            context = (context_class or self.context_class)(data)
        return self.render_with_context(context)

    def render(self, *, context=None, context_class=None, **data):
        return flatten(self.render_nested(context=context,
                                          context_class=context_class, **data))


if __name__ == '__main__':
    tpl = Template("""Hello,
        {% for i in x %}
            {{i}}: {{i - j.x - j.y }} {{i + j.x + j.y}}
            {% if i == 6 %}
                i is 6!
            {% endif %}
        {% endfor %}
    Goodbye!
    """)

    res = tpl.render(x=[2, 4, 6], j=dict(x=1, y=2))
    print(res)

    """
        {% if a > b %}
        hello
        {% endif %}
    """
