from ate.ate import Template


class TestInheritance:
    """ Inheritance of templates is implemented using the 'slot' and 'fill'
        statements
    """

    def test_simple(self):
        base = Template("HEAD {%content%}xxx{%endcontent%} FOOTER")
        final = Template("This is the body", parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_2levels(self):
        base = Template("HEAD {%content%}xxx{%endcontent%} FOOTER")
        first = Template("This is the body {% content %} yyy {% endcontent %}",
                         parent=base)
        second = Template("The end...", parent=first)
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
