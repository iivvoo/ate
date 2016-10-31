import pytest

from ate.tags import CompileStatement
from ate.ate import ParseContext, Template
from ate.exceptions import ParseError


class TestErrorHandling:

    def test_simple(self):
        tpl = ParseContext("{% nonexisting and unclosed")
        with pytest.raises(ParseError) as e:
            res, skip = CompileStatement(tpl)

        exc = e.value
        assert exc.pc.offset == 0
        assert exc.pc.code.startswith("{% nonexisting")
        line, col = exc.pc.position()
        assert line == 1
        assert col == 1

    def test_nested(self):
        tpl = ParseContext("""{% for i in 'abc' %}
    {%if } {{i}} {%endif%}
""")
        with pytest.raises(ParseError) as e:
            res, skip = CompileStatement(tpl)

        exc = e.value
        assert exc.pc.offset == 25
        assert exc.pc.code.startswith("{%if")
        line, col = exc.pc.position()
        assert line == 2
        assert col == 5

    def test_multi_line_indent(self):
        tpl = """Hello World

this is a  test
a         {%if }
more noise
...
"""
        with pytest.raises(ParseError) as e:
            Template(tpl)

        exc = e.value
        assert exc.pc.offset == 39
        assert exc.pc.code.startswith("{%if")
        line, col = exc.pc.position()
        assert line == 4
        assert col == 11

    def test_be_smart_about_closed(self):
        tpl = ParseContext("""{% for i in 'abc' %}
    {%if } {{i}} {%endif%}
{%endfor%}
""")
        with pytest.raises(ParseError) as e:
            res, skip = CompileStatement(tpl)

        exc = e.value
        assert exc.pc.offset == 48
        assert exc.pc.code.startswith("{%endfor")

        # import pdb; pdb.set_trace()
        line, col = exc.pc.position()
        assert line == 3
        assert col == 1

    def test_complex(self):
        tpl = """Hello World

        {% for i in abc%}
          x {{i}}
        {% endfor %}

        That's all!"""
        t = Template(tpl)
        t.render(abc="123")
