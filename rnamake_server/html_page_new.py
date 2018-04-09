from bs4 import BeautifulSoup

import glob
from html import *


def get_navbar(name, items, links, active="Home"):
    list_items = []
    for i, item in enumerate(items):
        if item == active:
            list_items.append(LItem("", "class=active",
                                    Link(item, "href=" + links[i])))
        else:
            list_items.append(LItem("",
                                    Link(item, "href="+links[i])))


    n = Navbar("class=navbar navbar-inverse navbar-fixed-top",
               Link(name, "href=#", "class=navbar-brand"),
               Div("class=collapse navbar-collapse",
                   LGroup("class=nav navbar-nav", *list_items)))

    return n


def get_meta_data():
     return  """
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="description" content="">
        <meta name="author" content="">"""


def get_dependent_files():
    files = [
        "/res/css/bootstrap.min.css",
        "/res/css/bootstrap-theme.min.css",
        "/res/css/theme.css",
        "/res/css/box_theme.css",
        "http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js",
        "/res/js/bootstrap.min.js",
        "/res/js/plotly-latest.min.js",
        "/res/js/index.js"]

    s = ""
    for f in files:
        if   f[-3:] == "css":
            s += "<link href=\""+f + "\" rel=\"stylesheet\">\n"
        elif f[-3:] == ".js":
            s += "<script src=\""+f + "\" ></script>\n"

    return s



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

        return BeautifulSoup(s, "html.parser").prettify(formatter='html')


def form_text():
    return """
            <form method='post' class="form-horizontal" action='/design_primers' enctype="multipart/form-data">
            <div class="input-group">
                <span class="input-group-btn">
                    <span class="btn btn-primary btn-file">
                        Select RNA PDB: <input type="file" name="pdb_file" />
                    </span>
                </span>
            </div>

    

        </form>
    
    """


def current_navbar(active="Home"):
    items = "Home Tutorial About".split()
    links = "/res/html/Design.html /res/html/Tutorial.html /res/html/About.html".split()
    n = get_navbar("RNAMake Server", items, links, active)
    return n


def current_form():
    d =  Div("class=input-group",
             Span("", "class=input-group-btn",
                  Span("Select RNA PDB: ",
                       "class=btn btn-primary btn-file",
                       Input("type=file", "name=pdb_file"))),
             Input("type=text", "class=form-control", "style=width: 40%"))

    form_args = ["method=post", "class=form-horizontal", "action=/design_primers", "enctype=multipart/form-data"]
    return Form(d, *form_args)


class BasicPage(HTMLPage):
    def __init__(self, title=None, logo=None):
        HTMLPage.__init__(self)
        self.head += get_meta_data()
        self.head += get_dependent_files()
        self.body += current_navbar()



class IndexPage(HTMLPage):
    def __init__(self, title=None, logo=None):
        HTMLPage.__init__(self)
        self.head += get_meta_data()
        self.head += get_dependent_files()

        self.body += current_navbar()

        b = Div("class=container",
                Div("class=jumbotron",
                    H1("Welcome!", "class=display-4")))

        self.body += b.get_html_str()
        self.body += current_form()



class ResultsPage(HTMLPage):
    def __init__(self, job_id, title=None, logo=None):
        HTMLPage.__init__(self)
        self.head += get_meta_data()
        self.head += get_dependent_files()

        self.body += current_navbar()
        self.body += H3("job: " + job_id)
        self.body += "<a href=/download/?dir_id=%s&data=all><button type=\"button\" \
                  class=\"btn btn-primary\">Download Everything</button></a>" % (job_id)
        self.body += "<br><br><br>"
        self.body += self.get_pdb_table(job_id)



    def get_pdb_table(self, job_id, max=10, rows=2, cols=5):
        imgs = glob.glob("data/" + job_id + "/design_*")
        divs = []
        for i in range(0, len(imgs)):
            if i >= max:
                break
            divs.append(
                Div("class=box",
                    Img("src=/" + imgs[i], "height=25%"),
                       Span("", "class=caption simple-caption",
                            H6("Design "+str(i)+"<br> Score: XXX\n"))))

        return Div("id=mainwrapper", *divs)







        #BasicPage()
#print BasicPage().to_str()



























