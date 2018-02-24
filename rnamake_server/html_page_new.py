from bs4 import BeautifulSoup

from html import *


def get_navbar(name, items, links, active="Home"):
    list_items = []
    for i, item in enumerate(items):
        if item == active:
            list_items.append(LItem(item, "href="+links[i], "class=active"))
        else:
            list_items.append(LItem(item, "href="+links[i]))


    n = Navbar("class=navbar navbar-inverse navbar-fixed-top",
               Link(name, "href=#", "class=navbar-brand"),
               Div("class=collapse navbar-collapse",
                   LGroup("class=nav navbar-nav", *list_items)))

    return n


def get_meta_data():
    return Block(
        """
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="description" content="">
        <meta name="author" content="">""")

def get_dependent_files():
    pass




class HTMLPage(object):
    def __init__(self):
        self.head, self.javascript, self.body = "", "", ""


    def to_str(self):
        s = """
        <html>
        <head>
        %s

        <script>
        %s
        </script>
        </head>
        <body>
        %s
        </body>
        </html> """ % (self.head, self.javascript, self.body)

        s = BeautifulSoup(s).prettify()

        return s


class BasicPage(HTMLPage):
    def __init__(self, title=None, logo=None):
        HTMLPage.__init__(self)
        items = "Home Tutorial About".split()
        links = "/res/html/Design.html /res/html/Tutorial.html /res/html/About.html"
        n = get_navbar("RNAMake Server", items, links)
        self.body += n.get_html_str()



print BasicPage().to_str()





