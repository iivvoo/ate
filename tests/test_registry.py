import pytest

from ate.ate import Registry
from ate.ate import StatementNotFound, StatementNotAllowed
from ate.ate import MainNode, StatementNode


@pytest.fixture
def registry():
    return Registry()


class TestTagRegistry:

    def test_empty_registry(self, registry):
        with pytest.raises(StatementNotFound):
            registry.find("foo", MainNode)

    def test_registry_found_nondirect_main(self, registry):
        """
            Nodes registered under the toplevel class without
            'direct' restriction can appear directly under the
            registered (main) node
            {%main%}
              {%foo%}
        """
        class FooStatementNode(StatementNode):
            pass

        m = MainNode("main")

        registry.register("foo", FooStatementNode, MainNode)
        assert registry.find("foo", m) == FooStatementNode

    def test_registry_found_nondirect_main_deep(self, registry):
        """
            Nodes registered under the toplevel class without
            'direct' restriction can appear anywhere
            {%main%}
              {%bar%}
                {%foo%}
            (foo registered under main)
        """
        class FooStatementNode(StatementNode):
            pass

        class BarStatementNode(StatementNode):
            pass

        m = MainNode("main")
        b = BarStatementNode("bar", parent=m)

        registry.register("foo", FooStatementNode, MainNode)
        registry.register("bar", BarStatementNode, MainNode)
        # import pdb; pdb.set_trace()
        assert registry.find("foo", b) == FooStatementNode

    def test_registry_found_nondirect_nonmain_deep(self, registry):
        """
            Nodes registered under a non-top class without
            'direct' restriction can appear anywhere under that node
            {%main%}
              {%bar%}
                {%foo%}
            (foo registered under bar)
        """
        class FooStatementNode(StatementNode):
            pass

        class BarStatementNode(StatementNode):
            pass

        m = MainNode("main")
        b = BarStatementNode("bar", parent=m)

        registry.register("foo", FooStatementNode, BarStatementNode)
        registry.register("bar", BarStatementNode, MainNode)
        assert registry.find("foo", b) == FooStatementNode

    def test_registry_found_nondirect_nonmain_deep_in_main(self, registry):
        """
            Nodes registered under a non-top class without
            'direct' restriction can't appear "above" that node
            {%main%}
              {%foo%}
              {%bar%}
            (foo registered under bar)
        """
        class FooStatementNode(StatementNode):
            pass

        class BarStatementNode(StatementNode):
            pass

        m = MainNode("main")
        BarStatementNode("bar", parent=m)

        registry.register("foo", FooStatementNode, BarStatementNode)
        registry.register("bar", BarStatementNode, MainNode)
        with pytest.raises(StatementNotAllowed):
            assert registry.find("foo", m) == FooStatementNode

    def test_registry_found_direct_main(self, registry):
        """
            Nodes registered under the toplevel class without
            'direct' restriction can appear directly under the
            registered (main) node
            {%main%}
              {%foo%}
        """
        class FooStatementNode(StatementNode):
            pass

        m = MainNode("main")

        registry.register("foo", FooStatementNode, MainNode, direct=True)
        assert registry.find("foo", m) == FooStatementNode

    def test_registry_found_indirect(self, registry):
        """
            Nodes registered under a non-top class without
            'direct' restriction can appear anywhere
            {%main%}
              {%bar%}
                {%foo%}
            (foo registered under bar)
        """
        class FooStatementNode(StatementNode):
            pass

        class BarStatementNode(StatementNode):
            pass

        m = MainNode("main")
        b = BarStatementNode("bar", parent=m)

        registry.register("foo", FooStatementNode,
                          BarStatementNode, direct=True)
        registry.register("bar", BarStatementNode, MainNode, direct=True)
        assert registry.find("foo", b) == FooStatementNode

    def test_registry_found_direct_main_deep(self, registry):
        """
            A node that must appear direcly under main cannot be
            in a deeper node
            {%main%}
              {%bar%}
                {%foo%}
            (foo registered under main, direct)
        """
        class FooStatementNode(StatementNode):
            pass

        class BarStatementNode(StatementNode):
            pass

        m = MainNode("main")
        b = BarStatementNode("bar", parent=m)

        registry.register("foo", FooStatementNode, MainNode, direct=True)
        registry.register("bar", BarStatementNode, MainNode, direct=True)

        with pytest.raises(StatementNotAllowed):
            assert registry.find("foo", b) == FooStatementNode

    def test_dual_else_direct(self, registry):
        """
            The else statement makes sense for both For and If, but only
            directly

            {%main%}
              {%if%}
                {%else%}
              {%for%}
                {%else%}
        """
        class IfStatementNode(StatementNode):
            pass

        class ForStatementNode(StatementNode):
            pass

        class IfElseStatementNode(StatementNode):
            pass

        class ForElseStatementNode(StatementNode):
            pass

        registry.register("if", IfStatementNode, MainNode)
        registry.register("for", ForStatementNode, MainNode)
        registry.register("else", IfElseStatementNode,
                          IfStatementNode, direct=True)
        registry.register("else", ForElseStatementNode,
                          ForStatementNode, direct=True)

        m = MainNode("main")
        ifnode = IfStatementNode("if", parent=m)
        fornode = ForStatementNode("for", parent=m)

        assert registry.find("else", ifnode) == IfElseStatementNode
        assert registry.find("else", fornode) == ForElseStatementNode
