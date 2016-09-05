from ate.ate import Template
from ate.ate import CompileStatement
from ate.ate import TextNode
from ate.ate import ExpressionNode
from ate.ate import BlockStatementNode


class TestMyTpl:

    def xtest_empty(self):
        res, skip = compile("")
        assert skip == 0
        assert len(res) == 0

    def xtest_multiline(self):
        tpl = """Hello
        world

        bye!"""
        res, skip = compile(tpl)
        assert skip == len(tpl)
        assert isinstance(res[0], TextNode)
        assert res[0].code == tpl

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
        res, skip = compile(tpl)
        assert skip == len(tpl)
        assert len(res) == 3
        assert isinstance(res[0], TextNode)
        assert isinstance(res[1], BlockStatementNode)
        assert isinstance(res[2], TextNode)

    def test_closing_spacing(self):
        res, skip = compile("{%for%}{%endfor%}")
        assert len(res) == 1

    def test_closing_spacing2(self):
        res, skip = compile("{%for%}{% endfor%}")
        assert len(res) == 1

    def test_closing_spacing3(self):
        res, skip = compile("{%for%}{%  endfor%}")
        assert len(res) == 1

    def test_closing_spacing4(self):
        res, skip = compile("{%for%}{%endfor %}")
        assert len(res) == 1

    def test_closing_spacing5(self):
        res, skip = compile("{%for%}{%endfor  %}")
        assert len(res) == 1

    def test_closing_spacing6(self):
        res, skip = compile("{%for%}{%  endfor  %}")
        assert len(res) == 1


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

    def xtest_else(self):
        tpl = Template("{%if bool%}TRUE{%else%}FALSE{%endif%}")
        assert tpl.render(bool=True) == "TRUE"
        assert tpl.render(bool=False) == "FALSE"