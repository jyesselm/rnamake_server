from bs4 import BeautifulSoup

def format_tag(tag, mods):
    s = "<" + tag + " "
    for k in mods:
        s += k + "=\"" + mods[k] + "\" "

    s += ">"
    return s

def parse_mods(tag_infos):
    all_mods = []
    for arg in tag_infos:
        spl = arg.split("=")
        all_mods.append(Mod(spl[0], " ".join(spl[1:])))

    return Mods(all_mods)


class Mod(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Mods(object):
    def __init__(self, mods):
        self.mods = {}
        for m in mods:
            self.mods[m.name] = m

    def __getitem__(self, name):
        return self.mods[name].value

    def __iter__(self):
        return self.mods.__iter__()


class HTML(object):
    def __init__(self, tag, *args):
        self.children = []
        self.tag = tag
        self.child_lookup = {}
        tag_infos = []
        for arg in args:
            if type(arg) == str:
               tag_infos.append(arg)
            elif type(arg) == HTML or isinstance(arg, HTML):
                self.add(arg)

        self.mods = parse_mods(tag_infos)


    def __getitem__(self, item):
        return self.child_lookup[item]


    def add(self, html_obj):
        self.children.append(html_obj)
        if html_obj.tag not in self.child_lookup:
            self.child_lookup[html_obj.tag] = [ html_obj ]

    def get_html_str(self):
        s = ""
        s += format_tag(self.tag, self.mods) + "\n"
        for c in self.children:
            s += c.get_html_str() + "\n"
        s += "</" + self.tag + ">"
        return s

    def get_pretty_str(self):
        return BeautifulSoup(self.get_html_str(), "html.parser").prettify(formatter='html')

    def __str__(self):
        return self.get_html_str()

    def __radd__(self, other):
        return other + str(self)


class HTMLSingle(HTML):
    def __init__(self, tag, *args):
        HTML.__init__(self, tag, *args)


    def get_html_str(self):
        s = ""
        s += format_tag(self.tag, self.mods) + "\n"
        return s

class HTMLText(HTML):
    def __init__(self, tag, text, *args):
        HTML.__init__(self, tag, *args)
        self.text = text

    def get_html_str(self):
        s = ""
        s += format_tag(self.tag, self.mods) + "\n"
        s += self.text + " "
        for c in self.children:
            s += c.get_html_str() + "\n"
        s += "</" + self.tag + ">"
        return s


class Block(HTMLText):
    def __init__(self, text):
        HTMLText.__init__(self, "", text)

    def get_html_str(self):
        return self.text


#### non text elements

class Div(HTML):
    def __init__(self, *args):
        HTML.__init__(self, "div", *args)


class Form(HTML):
    def __init__(self, *args):
        HTML.__init__(self, "form", *args)


class Select(HTML):
    def __init__(self, *args):
        HTML.__init__(self, "select", *args)


class LGroup(HTML):
    def __init__(self, *args):
        HTML.__init__(self, "ul", *args)


class Table(HTML):
    def __init__(self, *args):
        HTML.__init__(self, "table", *args)


class Thead(HTML):
    def __init__(self, *args):
        HTML.__init__(self, "Thead", *args)


class Tr(HTML):
    def __init__(self, *args):
        HTML.__init__(self, "tr", *args)


### text elements

class H1(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "h1", text, *args)


class H2(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "h2", text, *args)


class H3(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "h3", text, *args)


class H4(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "h4", text, *args)


class H5(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "h5", text, *args)


class H6(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "h6", text, *args)


class Span(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "span", text, *args)


class Button(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "button", text, *args)


class Link(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "a", text, *args)


class Option(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "option", text, *args)


class Label(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "label", text, *args)


class LItem(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "li", text, *args)


class Td(HTMLText):
    def __init__(self, text, *args):
        HTMLText.__init__(self, "td", text, *args)


# html singles

class Linebreak(HTMLSingle):
    def __init__(self, *args):
        HTMLSingle.__init__(self, "br", *args)

class Img(HTMLSingle):
    def __init__(self, *args):
        HTMLSingle.__init__(self, "img", *args)

class Input(HTMLSingle):
    def __init__(self, *args):
        HTMLSingle.__init__(self, "input", *args)


#########################


class Navbar(HTML):
    def __init__(self, *args):
        HTML.__init__(self, "div", *args)


"""class Link(HTML):
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
"""

class FileLink(HTML):
    def __init__(self, *args):
        HTML.__init__(self, *args)





#n.add(Link("nav_header", "Navbar", "#", cls="navbar-brand"))
#n.add(Div("div1", "class=collapse navbar-collapse",
#          Div("div2")))



