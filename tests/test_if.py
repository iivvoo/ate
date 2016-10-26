import pytest

from ate.ate import Template

from ate.exceptions import StatementNotAllowed


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
