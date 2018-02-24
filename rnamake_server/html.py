from bs4 import BeautifulSoup

def format_tag(tag, name="", cls="", style="", role="", href=""):
    s = "<" + tag + " "
    if len(name) > 0:
        s += "name=\"" + name + "\" "
    if len(cls) > 0:
        s += "class=\"" + cls + "\" "
    if len(style) > 0:
        s += "style=\"" + style + "\" "
    if len(role) > 0:
        s += "role=\"" + role + "\" "
    if len(href) > 0:
        s += "href=\"" + href + "\" "
    s += ">"
    return s

class HTML(object):
    def __init__(self, *args):
        self.children = []
        self.tag = "div"
        self.cls = ""
        self.style = ""
        self.role = ""
        self.name = ""
        self.href = ""
        self.child_lookup = {}
        for arg in args:
            if type(arg) == str:
               self._parse_str_arg(arg)
            elif type(arg) == HTML or isinstance(arg, HTML):
                self.add(arg)


    def _parse_str_arg(self, s):
        spl = s.split("=")
        if len(spl) != 2:
            raise ValueError("must have an equals")
        if spl[0] == "class":
            self.cls = spl[1]
        if spl[0] == "style":
            self.style = spl[1]
        if spl[0] == "role":
            self.role = spl[1]
        if spl[0] == "href":
            self.href = spl[1]

    def __getitem__(self, item):
        return self.child_lookup[item]


    def add(self, html_obj):
        self.children.append(html_obj)
        if html_obj.tag not in self.child_lookup:
            self.child_lookup[html_obj.tag] = [ html_obj ]

    def get_html_str(self):
        s = ""
        s += format_tag(self.tag, self.name, self.cls, self.style, self.role) + "\n"
        for c in self.children:
            s += c.get_html_str() + "\n"
        s += "</" + self.tag + ">"
        return s

    def get_pretty_str(self):
        return BeautifulSoup(self.get_html_str(), "html.parser").prettify(formatter='html')

class Div(HTML):
    def __init__(self, *args):
        HTML.__init__(self, *args)
        self.tag = "div"

class Block(HTML):
    def __init__(self, text):
        HTML.__init__(self)
        self.text = text

    def get_html_str(self):
        return self.text


class Navbar(HTML):
    def __init__(self, *args):
        HTML.__init__(self, *args)
        self.tag = "div"
        self.role = "navigation"

class Link(HTML):
    def __init__(self, text, *args):
        HTML.__init__(self, *args)
        self.text = text
        self.tag = "a"

    def get_html_str(self):
        s = ""
        s += format_tag(self.tag, self.name, self.cls, self.style, self.role, self.href) + "\n"
        s += self.text
        s += "</a>"
        return s

class LItem(HTML):
    def __init__(self, text, *args):
        HTML.__init__(self, *args)
        self.text = text
        self.tag = "li"

    def get_html_str(self):
        s = ""
        s += format_tag(self.tag, self.name, self.cls, self.style, self.role) + "\n"
        if self.href != "":
            s += format_tag("a", href=self.href)
        s += self.text
        if self.href != "":
            s += "</a>"
        s += "</" + self.tag + ">"
        return s

class LGroup(HTML):
    def __init__(self, *args):
        HTML.__init__(self, *args)
        self.tag = "ul"



"""n = Navbar("class=navbar navbar-inverse navbar-fixed-top",
           Link("Navbar", "href=#", "class=navbar-brand"),
           Div("class=collapse navbar-collapse",
               LGroup("class=nav navbar-nav",
                      LItem("Home", "href=/res/html/Design.html","class=active"),
                      LItem("Tutorial", "href=/res/html/Tutorial.html"),
                      LItem("About", "href=/res/html/About.html"))))"""

#n.add(Link("nav_header", "Navbar", "#", cls="navbar-brand"))
#n.add(Div("div1", "class=collapse navbar-collapse",
#          Div("div2")))



