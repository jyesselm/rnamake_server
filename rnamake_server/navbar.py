from html_page import HTMLElement
from bs4 import BeautifulSoup

def get_nav_bar():
    return """<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/res/html/Design.html">&nbsp;&nbsp;RNA Redesign&nbsp;&nbsp;</a>

        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="/res/html/Design.html">Home</a></li>
            <li><a href="/res/html/Tutorial.html">Tutorial</a></li>
            <li><a href="/res/html/About.html">About</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </div>
    """


class NavBarHeader(HTMLElement):
    def __init__(self, name, c="navbar-header", spacers=3, link=""):
        self.head, self.javascript, self.body = "", "", ""
        self.body = """
            <div class="%s">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                    <span class="sr-only">Toggle navigation</span>

        """ % (c)

        for i in range(spacers):
            self.body += "<span class=\"icon-bar\"></span>\n"
        self.body += "</button>\n"
        self.body += """<a class="navbar-brand" href="%s">&nbsp;&nbsp;%s&nbsp;&nbsp;</a></div>""" % (link, name)


        self.body = BeautifulSoup(self.body, "html.parser").prettify(formatter='html')


class NavBar(HTMLElement):
    def __init__(self, elements, header=None, c="navbar navbar-inverse navbar-fixed-top"):
        self.head, self.javascript, self.body = "", "", ""
        self.body = """<div class="%s" role="navigation">""" % (c)

        if header is not None:
            self.body += header.body
            self.head += header.head
            self.javascript += header.javascript


