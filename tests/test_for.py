from ate.ate import Template


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
