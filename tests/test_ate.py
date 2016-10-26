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

    def test_loop(self):
        tpl = Template("{% for i in seq%}"
                       "{%if loop.first%}{{i}} is first{%endif%}"
                       "{%if loop.last%}{{i}} is last{%endif%}"
                       "{{i}}{{loop.index}}-{{loop.index0}}"
                       "{%endfor%}"
                       )
        res = tpl.render(seq="abcde")
        assert res == "a is firsta0-1b1-2c2-3d3-4e is laste4-5"


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


class TestInheritance:

    def test_simple(self):
        """
            Assume base/extended template definition is defined outside
            of template. So no need for {% extend %}

            Use defaults. {%content%} means the defaul ("main"?) content block
            a template without an explicit block will render into the default
            block.

            Multiple slots / blocks (and proper extending) should be supported
            eventually but the simplest cases first

            moet je eerst de base renderen en dan de child invoegen?
            Of "letterlijk" samenvoegen?

            Een template kan een parent hebben (en dat weer recursief).
            Renderen gebeurt altijd vanuit de parent, en de parent kijkt
            daarbij naar z'n "directe" child om content blokken in te vullen.

            De parent gaat vervolgens recursief naar beneden wandelen, waarbij
            'child' telkens verandert.


        """
        base = Template("HEAD {%content%}xxx{%endcontent%} FOOTER")
        final = Template("This is the body", parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_2levels(self):
        base = Template("HEAD {%content%}xxx{%endcontent%} FOOTER")
        first = Template("This is the body {% content %} yyy {% endcontent %}",
                         parent=base)
        second = Template("The end...", parent=first)
        # import pdb; pdb.set_trace()
        res = second.render()
        assert res == "HEAD This is the body The end... FOOTER"

    def test_explicit1(self):
        base = Template("HEAD {%content main%}xxx{%endcontent%} FOOTER")
        final = Template("This is the body", parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_explicit2(self):
        base = Template("HEAD {%content main%}xxx{%endcontent%} FOOTER")
        final = Template("{%block main%}This is the body{%endblock%}",
                         parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_explicit3(self):
        base = Template("HEAD {%content main%}xxx{%endcontent%} FOOTER")
        final = Template("{%block main%}This is the body{%endblock%}"
                         "{%block other%}Other block{%endblock%}",
                         parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_nondefault(self):
        base = Template("HEAD {%content foo%}xxx{%endcontent%} FOOTER")
        final = Template(
            "{%block foo%}This is the body{%endblock%}", parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_missing(self):
        base = Template("HEAD {%content foo%}xxx{%endcontent%} FOOTER")
        final = Template(
            "{%block main%}This is the body{%endblock%}", parent=base)
        res = final.render()
        assert res == "HEAD xxx FOOTER"

    def test_context_inheritance(self):
        base = Template("HEAD {% for i in '123' %}"
                        "{%content%}xxx{%endcontent%}"
                        "{%endfor%} FOOTER")
        final = Template("body {{i}}", parent=base)
        res = final.render()
        assert res == "HEAD body 1body 2body 3 FOOTER"

    def test_multi_block(self):
        base = Template("HEAD {%content main%}xxx{%endcontent%} - "
                        "{% content bar %}yyy{%endcontent%} FOOTER")
        final = Template("Hello "
                         "{%block main %}This is the main block"
                         "{% endblock %} and "
                         "{%block bar %}this is the bar block"
                         "{%endblock %}", parent=base)
        res = final.render()
        assert res == "HEAD This is the main block - this is the bar block FOOTER"

    def test_multi_block_sideeffect(self):
        """ if the child does not explicitly define a block, it will be
            used for any / all blocks """
        base = Template("HEAD {%content main%}xxx{%endcontent%} - "
                        "{% content bar %}yyy{%endcontent%} FOOTER")
        final = Template("Hello", parent=base)
        res = final.render()
        assert res == "HEAD Hello - Hello FOOTER"

    def test_total_madness1(self):
        base = Template("HEAD {%content a%} aa {% endcontent %}"
                        "{%for i in '123'%}"
                        "{%content b %}{%endcontent%}"
                        "{%endfor%}"
                        "FOOTER")
        c1 = Template("{%block a%}A{%endblock%}"
                      "noise"
                      "{%block b%}"
                      "{{i}}{%content c%}..{%endcontent%}"
                      "{%endblock%}",
                      parent=base)
        c2 = Template("Default", parent=c1)

        res = c2.render()
        assert res == "HEAD A1Default2Default3DefaultFOOTER"
