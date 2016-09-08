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

- rename
- expressions, statements
- {%else%}
- {# comments #}
- sensible error reports

"""
from simpleeval import SimpleEval


from .tags import MainNode


class Context:
    """
        Make it a context manager so context get popped automatically?

        with context.add({'a':1}):
            ....

    """

    def __init__(self, data):
        self.stack = [data]
        self.evaluator = SimpleEval(names=self.name_handler)

    def name_handler(self, node):
        name = node.id
        for ctx in reversed(self.stack):
            try:
                return ctx[name]
            except KeyError:
                pass
        raise NameError(name)

    def push(self, data):
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


class Template:

    def __init__(self, code):
        self.code = code
        self.mainnode = self.compile()
        self.rendered = []

    def compile(self):
        node = MainNode(type="main")
        node.compile(self.code)
        return node

    def render_nested(self, **data):
        context = Context(data)
        return self.mainnode.render(context)

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
