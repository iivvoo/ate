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
        assert line == 1
        assert col == 5

    def xtest_be_smart_about_closed(self):
        tpl = ParseContext("""{% for i in 'abc' %}
    {%if } {{i}} {%endif%}
{%endfor%}
""")
        with pytest.raises(ParseError) as e:
            res, skip = CompileStatement(tpl)

        exc = e.value
        assert exc.pc.offset == 25
        assert exc.pc.code.startswith("{%if")

        line, col = exc.pc.position()
        assert line == 1
        assert col == 5

    def test_complex(self):
        tpl = """Hello World

        {% for i in abc%}
          x {{i}}
        {% endfor %}

        That's all!"""
        t = Template(tpl)
        t.render(abc="123")
