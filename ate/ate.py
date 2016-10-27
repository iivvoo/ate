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
from simpleeval import SimpleEval
from contextlib import contextmanager

from .tags import MainNode


class Context:
    """
        Make it a context manager so context get popped automatically?

        with context.add({'a':1}):
            ....

    """

    def __init__(self, data):
        self.stack = [data]
        self.children = []
        self.evaluator = SimpleEval(names=self.name_handler)

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
        return self.evaluator.eval(expr)


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

        Idee:

        Code is gewrapt in ParseContext. Als je gaat slicen dan krijg je een nieuwe
        context die weet wat z'n relatieve positie is.

        Ga uit dat python string slicing efficient is
    """

    def __init__(self, code, offset=0, parent=None):
        self.code = code
        self.offset = offset
        self.parent = parent

    def __len__(self):
        return len(self.code) - self.offset

    def __getitem__(self, i):
        if isinstance(i, slice):
            offset = i.start or 0
            return ParseContext(self.code[i], offset=self.offset + offset,
                                parent=self)
        return self.code[i]


class Template:

    def __init__(self, code, parent=None):
        self.code = code
        self.mainnode = self.compile()
        self.rendered = []
        self.parent = parent

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

    def render_nested(self, **data):
        context = Context(data)
        return self.render_with_context(context)

    def render(self, **data):
        return flatten(self.render_nested(**data))


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
