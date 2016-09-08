import pytest

from ate.ate import Template
from ate.tags import CompileStatement
from ate.tags import TextNode
from ate.tags import ExpressionNode
from ate.tags import BlockStatementNode
from ate.tags import MainNode
from ate.tags import ForBlockStatementNode

from ate.exceptions import StatementNotAllowed


class TestMyTpl:

    def test_empty(self):
        template = Template("")
        assert isinstance(template.mainnode, MainNode)
        assert len(template.mainnode.nodes) == 0

    def test_multiline(self):
        tpl = """Hello
        world

        bye!"""
        template = Template(tpl)
        assert isinstance(template.mainnode, MainNode)
        assert isinstance(template.mainnode.nodes[0], TextNode)
        assert template.mainnode.nodes[0].text == tpl

    def test_statement(self):
        tpl = "{{hello}}"
        res, skip = CompileStatement(tpl)
        assert skip == len(tpl)
        assert isinstance(res, ExpressionNode)
        assert res.expression == "{{hello}}"

    def test_block(self):
        tpl = "{% for i in abc%} x {% endfor %}"
        # import pdb; pdb.set_trace()
        res, skip = CompileStatement(tpl)
        assert skip == len(tpl)
        assert isinstance(res, BlockStatementNode)
        assert res.type == "for"
        assert res.expression == "i in abc"
        assert res.code == tpl

        assert len(res.nodes) == 1
        assert isinstance(res.nodes[0], TextNode)
        assert res.nodes[0].text == " x "

    def test_complex(self):
        tpl = """Hello World

        {% for i in abc%}
          x {{i}}
        {% endfor %}

        That's all!"""
        # import pdb; pdb.set_trace()
        t = Template(tpl)
        assert len(t.mainnode.nodes) == 3
        nodes = t.mainnode.nodes
        assert isinstance(nodes[0], TextNode)
        assert isinstance(nodes[1], BlockStatementNode)
        assert isinstance(nodes[2], TextNode)

    def test_closing_spacing(self):
        tn = ForBlockStatementNode("for")
        index = tn.compile("{%for%}{%endfor%}", len("{%for%}"))
        assert index == 17

    def test_closing_spacing2(self):
        tn = ForBlockStatementNode("for")
        index = tn.compile("{%for%}{% endfor%}", len("{%for%}"))
        assert index == 18

    def test_closing_spacing3(self):
        tn = ForBlockStatementNode("for")
        index = tn.compile("{%for%}{%  endfor%}", len("{%for%}"))
        assert index == 19

    def test_closing_spacing4(self):
        tn = ForBlockStatementNode("for")
        index = tn.compile("{%for%}{%endfor %}", len("{%for%}"))
        assert index == 18

    def test_closing_spacing5(self):
        tn = ForBlockStatementNode("for")
        index = tn.compile("{%for%}{%endfor  %}", len("{%for%}"))
        assert index == 19

    def test_closing_spacing6(self):
        tn = ForBlockStatementNode("for")
        index = tn.compile("{%for%}{%  endfor  %}", len("{%for%}"))
        assert index == 21


class TestTemplateRender:

    def test_render_text(self):
        tpl = Template("Hello World\n"
                       "\n"
                       "{% for i in abc%}\n"
                       "  x {{i}}\n"
                       "{% endfor %}\n"
                       "\n"
                       "That's all!")
        rendered = tpl.render_nested(i=1, abc=[1])
        # import pdb;pdb.set_trace()
        assert rendered[0] == "Hello World\n\n"
        assert rendered[1][0] == "\n  x "
        assert rendered[1][2] == "\n"
        assert rendered[2] == "\n\nThat's all!"


class TestStatementEval:

    def test_interpolation(self):
        tpl = Template("{{i}}")
        assert tpl.render(i=10) == "10"
        assert tpl.render(i=0) == "0"
        assert tpl.render(i=-10) == "-10"
        assert tpl.render(i="hello") == "hello"

    def test_expression(self):
        tpl = Template("{{i + j}}")
        assert tpl.render(i=10, j=5) == "15"
        assert tpl.render(i="Hello", j="World") == "HelloWorld"


class TestForBlock:

    def test_simple(self):
        tpl = Template("{%for i in j%}{{i}}{% endfor %}")
        assert tpl.render(j="a") == "a"
        assert tpl.render(j=[1, 2, 3]) == "123"

    def test_context_stacking(self):
        """ this is more of a context feature """
        tpl = Template("{%for i in j%}{{i}}{%endfor%}{{i}}")
        assert tpl.render(i="z", j=["a"]) == "az"


class TestIfBlock:

    def test_simple(self):
        tpl = Template("{%if bool%}TRUE{%endif%}")
        assert tpl.render(bool=True) == "TRUE"
        assert tpl.render(bool=False) == ""

    def test_else(self):
        tpl = Template("{%if bool%}TRUE{%else%}FALSE{%endif%}")
        assert tpl.render(bool=True) == "TRUE"
        assert tpl.render(bool=False) == "FALSE"

    def test_toplevel_else(self):
        """ else cannot be used by itself """
        with pytest.raises(StatementNotAllowed):
            Template("{%else%}").render()
