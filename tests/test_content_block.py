from ate.ate import Template


class TestInheritance:
    """ Inheritance of templates is implemented using the 'slot' and 'fill'
        statements
    """

    def test_simple(self):
        base = Template("HEAD {%slot%}xxx{%endslot%} FOOTER")
        final = Template("This is the body", parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_2levels(self):
        base = Template("HEAD {%slot%}xxx{%endslot%} FOOTER")
        first = Template("This is the body {% slot %} yyy {% endslot %}",
                         parent=base)
        second = Template("The end...", parent=first)
        res = second.render()
        assert res == "HEAD This is the body The end... FOOTER"

    def test_explicit1(self):
        base = Template("HEAD {%slot main%}xxx{%endslot%} FOOTER")
        final = Template("This is the body", parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_explicit2(self):
        base = Template("HEAD {%slot main%}xxx{%endslot%} FOOTER")
        final = Template("{%fill main%}This is the body{%endfill%}",
                         parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_explicit3(self):
        base = Template("HEAD {%slot main%}xxx{%endslot%} FOOTER")
        final = Template("{%fill main%}This is the body{%endfill%}"
                         "{%fill other%}Other fill{%endfill%}",
                         parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_nondefault(self):
        base = Template("HEAD {%slot foo%}xxx{%endslot%} FOOTER")
        final = Template(
            "{%fill foo%}This is the body{%endfill%}", parent=base)
        res = final.render()
        assert res == "HEAD This is the body FOOTER"

    def test_missing(self):
        base = Template("HEAD {%slot foo%}xxx{%endslot%} FOOTER")
        final = Template(
            "{%fill main%}This is the body{%endfill%}", parent=base)
        res = final.render()
        assert res == "HEAD xxx FOOTER"

    def test_context_inheritance(self):
        base = Template("HEAD {% for i in '123' %}"
                        "{%slot%}xxx{%endslot%}"
                        "{%endfor%} FOOTER")
        final = Template("body {{i}}", parent=base)
        res = final.render()
        assert res == "HEAD body 1body 2body 3 FOOTER"

    def test_multi_fill(self):
        base = Template("HEAD {%slot main%}xxx{%endslot%} - "
                        "{% slot bar %}yyy{%endslot%} FOOTER")
        final = Template("Hello "
                         "{%fill main %}This is the main block"
                         "{% endfill %} and "
                         "{%fill bar %}this is the bar block"
                         "{%endfill %}", parent=base)
        res = final.render()
        assert res == "HEAD This is the main block - this is the bar block FOOTER"

    def test_multi_fill_sideeffect(self):
        """ if the child does not explicitly define a fill, it will be
            used for any / all slots """
        base = Template("HEAD {%slot main%}xxx{%endslot%} - "
                        "{% slot bar %}yyy{%endslot%} FOOTER")
        final = Template("Hello", parent=base)
        res = final.render()
        assert res == "HEAD Hello - Hello FOOTER"

    def test_total_madness1(self):
        base = Template("HEAD {%slot a%} aa {% endslot %}"
                        "{%for i in '123'%}"
                        "{%slot b %}{%endslot%}"
                        "{%endfor%}"
                        "FOOTER")
        c1 = Template("{%fill a%}A{%endfill%}"
                      "noise"
                      "{%fill b%}"
                      "{{i}}{%slot c%}..{%endslot%}"
                      "{%endfill%}",
                      parent=base)
        c2 = Template("Default", parent=c1)

        res = c2.render()
        assert res == "HEAD A1Default2Default3DefaultFOOTER"

    def test_attraction_marker(self):
        base = Template("HEAD {% slot content %}xxx{% endslot %} FOOTER")
        final = Template("<<MARKER>>", parent=base)
        res = final.render()
        assert res == "HEAD <<MARKER>> FOOTER"
