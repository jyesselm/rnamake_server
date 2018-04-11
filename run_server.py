import cherrypy
import pandas as pd
from cherrypy.lib.static import serve_file
from jinja2 import Environment, FileSystemLoader


import os
import random
import string
import sys
import shutil
import subprocess
import glob
import time

from collections import namedtuple

import rnamake_server.html_page
from rnamake_server import html_page_new
from rnamake_server import navbar

DesignImage = namedtuple('DesignImage', ['path', 'name'])
DesignInfo = namedtuple('DesignInfo', ['img_path', 'design_num', 'score',
                                       'eterna_score', 'sequence', 'structure', 'motifs_used'])
MotifInfo = namedtuple('MotifInfo', ['name', 'num'])


MEDIA_DIR = os.path.join(os.path.abspath("."))
DATA_BASE_DIR = MEDIA_DIR + "/data/"

j2_env = Environment(loader=FileSystemLoader(MEDIA_DIR),
                     trim_blocks=True)

class BasePage(rnamake_server.html_page.HTMLPage):
    def __init__(self):
       super(BasePage, self).__init__()
       self.add_element ( rnamake_server.html_page.HTMLFileTemplate("head.html") )
       self.add_element ( rnamake_server.html_page.HTMLFileTemplate("navbar.html") )


class ResultsWaitingPage(BasePage):
    def __init(self):
       super(ResultsWaitingPage, self).__init__()

    def _get_job_pos(self, data_dir):
        f = open(MEDIA_DIR + '/jobs.dat')
        lines = f.readlines()
        f.close()

        for i, l in enumerate(lines):
            if data_dir in l:
                return i

    def _remove_job(self, data_dir):
        f = open(MEDIA_DIR + '/jobs.dat')
        lines = f.readlines()
        f.close()

        f = open(MEDIA_DIR + '/jobs.dat', 'w')
        for l in lines:
            if data_dir in l:
                continue
            f.write(l)

        f.close()

    def _progress_bar_status(self, data_dir):
        path = DATA_BASE_DIR + data_dir + "/start.pdb"
        if not os.path.isfile(path):
            job_pos = self._get_job_pos(data_dir)
            return ["Queued, "+str(job_pos) + " jobs ahead", 0]

        path = DATA_BASE_DIR + data_dir + "/S_0001.pdb"
        if not os.path.isfile(path):
            return ["Running", 50]

	    return ["Generating Results Page", 90]

    def _is_pdb_valid(self, data_dir):
        os.chdir(DATA_BASE_DIR + data_dir)
        subprocess.call("make_rna_rosetta_ready.py -remove_ions rna.pdb",
                        shell=True)

        f = open("rna_RNA.pdb")
        lines = f.readlines()
        f.close()
        if len(lines) == 0:
            return -1

        pos = 4
        spl = lines[0].split()
        try:
            num = int(spl[pos])
        except:
            pos = 5

        nums = []
        for l in lines:
            spl = l.split()
            num = int(spl[pos])
            if num not in nums:
                nums.append(num)

        os.chdir(MEDIA_DIR)
        if len(nums) > 100:
            return 0
        else:
            return 1

    def render(self, data_dir):
        try:
            status, percent = self._progress_bar_status(data_dir)
        except:
            status, percent = "Generating Results Page", 90

        if percent == 0:
            if not os.path.isfile(DATA_BASE_DIR+data_dir+'/rna_RNA.pdb'):
                result = self._is_pdb_valid(data_dir)
                if result == -1:
                    status = "Error: not a valid PDB"
                    percent = -1

                elif result == 0:
                    status = "Error: RNA larger then 100nt"
                    percent = -1

                if percent == -1:
                    f = open(DATA_BASE_DIR+data_dir+'/ERROR', 'w')
                    f.write(status+"\n")
                    f.close()

        if os.path.isfile(DATA_BASE_DIR+data_dir+'/ERROR'):
            percent = -1
            f = open(DATA_BASE_DIR+data_dir+'/ERROR')
            lines = f.readlines()
            f.close()
            status = lines[0]

        if percent == -1:
            self._remove_job(data_dir)
            title = "<H1>"+status+"</H1>"
            progress_bar =  rna_design.html_page.HTMLPage()
        else:
            title = "<H1> Job Status: %s</H1>" % (status)
            progress_bar =  rna_design.html_page.ProgressBar(percent)
        waiting_table = ""

        body = """
        <div class="container">
        %s
        %s
        %s
        </div>
        """ % (title, progress_bar.body, waiting_table)

        self.body += body
        self.javascript += """
                setTimeout(function(){
                window.location.reload(1);
                 }, 60000);
        """

        return percent


def is_valid_name(input, char_allow, length):

    if len(input) <= length: return 0
    src = ''.join([string.digits, string.ascii_letters, char_allow])
    for char in input:
        if char not in src: return 0
    return 1


def is_valid_email(input):

    input_split = input.split("@")
    if len(input_split) != 2: return 0
    if not is_valid_name(input_split[0], ".-_", 2): return 0
    input_split = input_split[1].split(".")
    if len(input_split) == 1: return 0
    for char in input_split:
        if not is_valid_name(char, "", 1): return 0
    return 1

def get_js_native_recovery_chart(path):
    f = open(path)
    lines = f.readlines()
    f.close()

    s = """ var chart1 = new CanvasJS.Chart("NativeRecovery",
    {
      title:{
        text: "Native Sequence Recovery"
      },
      axisY: {
        title: "Native Recovery",
        maximum: 1.00,
        interlacedColor: "#F8F1E4",
        tickLength: 10,
        labelFontSize: 25,
        interval: 0.25
      },

      axisX: {
        title: "Residues"
      },
      data: [
      {
        type: "column",
        dataPoints: [
    """
    i = 10
    colors = {
        'g' : "Red",
        'c' : "Green",
        "a" : "Orange",
        "u" : "Blue"
    }

    lines.pop()
    lines.pop()
    lines.pop()
    lines.pop()
    lines.pop()

    for l in lines:
        spl = l.split()
        color = colors[spl[0][0].lower()]
        s += "{ x: " + str(i) + ", y: "+ str(spl[-2]) + ", label: " +\
            "\""+l[0].upper()+l[1:5].lstrip()+"\"" + ", color: \""+color+"\" },\n"
        i += 10

    s += """ ]
      }
      ]
    });

    chart1.render();
    chart1 = {}
    """

    return s

def get_js_energy_vs_sequence_identity(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    lines.pop(0)

    min_energy = 10000
    max_energy = -1000

    for l in lines:
        spl = l.split()
        energy = float(spl[1])
        if energy < min_energy:
            min_energy = energy
        if energy > max_energy:
            max_energy = energy

    min_energy = min_energy - min_energy*0.05
    max_energy = max_energy - max_energy*0.05

    s = """ var chart2 = new CanvasJS.Chart("EnergyScatter",
    {
      title:{
        text: "Sequence Recovery vs Rosetta Energy"
      },
      axisY: {
        title: "Rosetta Energy",
        maximum: """ + str(round(max_energy)) + ",\n" + \
        "minimum: " + str(round(min_energy))  + ",\n" + \
      """
      },

      axisX: {
        title: "Sequence Recovery (%)",
        interval: 5,
        intervalType: "number",
        valueFormatString: "##.#"
      },
      data: [
      {
        type: "scatter",
        dataPoints: [
    """
    i = 10

    for l in lines:
        spl = l.split()
        energy = spl[1]
        recovery = spl[3]
        s += "{ x: " + recovery + ", y: "+ energy + ", toolTipContent: \"" + spl[0] + "\"}," + "\n"

    s += """ ]
      }
      ]
    });

    chart2.render();
    chart2 = {}
    """

    return s


def format_pdb_num(num):
    s = "S_"

    if num < 1000:
        s += "0"
    if num < 100:
        s += "0"
    if num < 10:
        s += "0"
    s += str(num)
    return s + ".pdb"


def get_cluster_table(job_id):
    # TODO consider putting them on multiple rows
    s = "<div><table><tr>"

    for i in range(5):
        s += "<td><img src=/data/"+job_id+"/cluster_"+str(i)+".png height=25%></td>"

    s += "</tr></table></div>"
    return s

def get_js_score_plot(df):
    y = "[ " + ",".join(str(x) for x in df.opt_score) + "]"
    x = "[ " + ",".join(str(i+1) for i, x in enumerate(df.opt_score)) + "]"

    s = """
    var trace = { 
        x : %s, 
        y: %s,
        type: "line",
        marker : {
            opacity: 0.5, 
            line: {
                color: 'rbg(8,48,107)',
                width: 1.5
            }
            
        }
        
    };
    var layout = {
        autosize: false,
        width: 400,
        height: 400,  
        title: "Scores (Lower is better)",
        xaxis: {
            title: 'Design Number',
            showgrid: false,
            showline: true

        },
        yaxis: {
            title: 'Score',
            showgrid: false,
            showline: true

        },
        margin: {
            l : 60
        }
    };
    
    Plotly.newPlot('score_plot', [trace], layout);
    """ % (x, y )
    return s

def get_js_length_plot(df):
    y = "[ " + ",".join(str(len(x)) for x in df.opt_sequence) + "]"
    x = "[ " + ",".join(str(i + 1) for i, x in enumerate(df.opt_sequence)) + "]"

    s = """
    var trace = { 
        x : %s, 
        y: %s,
        type: "line",
        marker : {
            opacity: 0.5, 
            line: {
                color: 'rbg(8,48,107)',
                width: 1.5
            }

        }

    };
    var layout = {
        autosize: false,
        width: 400,
        height: 400,  
        title: "Length",
        xaxis: {
            title: 'Design Number',
            showgrid: false,
            showline: true

        },
        yaxis: {
            title: '# of Residues',
            showgrid: false,
            showline: true

        },
          margin: {
            l : 60
        }
    };

    Plotly.newPlot('length_plot', [trace], layout);
    """ % (x, y)
    return s

def get_js_eterna_score(df):
    y = "[ " + ",".join(str(x) for x in df.eterna_score) + "]"
    x = "[ " + ",".join(str(i + 1) for i, x in enumerate(df.eterna_score)) + "]"

    s = """
    var trace = { 
        x : %s, 
        y: %s,
        type: "line",
        marker : {
            opacity: 0.5, 
            line: {
                color: 'rbg(8,48,107)',
                width: 1.5
            }

        }

    };
    var layout = {
        autosize: false,
        width: 400,
        height: 400,  
        title: "Eterna Score (Larger is better)",
        xaxis: {
            title: 'Design Number',
            showgrid: false,
            showline: true

        },
        yaxis: {
            title: 'Eterna Score',
            showgrid: false,
            showline: true

        },
          margin: {
            l : 60
        }
    };

    Plotly.newPlot('eterna_plot', [trace], layout);
    """ % (x, y)
    return s

def get_design_infos(df, job_id):
    design_infos = []
    count = 1
    for i, row in df.iterrows():
        structure = "".join(["." for x in row.opt_sequence])
        motif_uses = []
        spl = row.motifs_uses.split(";")
        for e in spl[:-1]:
            if e[0] == "H":
                continue
            motif_uses.append(MotifInfo(e, count))
            count += 1

        design_infos.append(
            DesignInfo("/data/"+job_id+"/design_"+str(row.design_num)+".png",
                       row.design_num,
                       row.opt_score,
                       row.eterna_score,
                       row.opt_sequence,
                       structure,
                       motif_uses))
    return design_infos


class rest:

    @cherrypy.expose
    def index(self):
        index =  j2_env.get_template("res/templates/index.html")
        return index.render()

    @cherrypy.expose
    def about(self):
        about = j2_env.get_template("res/templates/about.html")
        return about.render()


    @cherrypy.expose
    def design_scaffold(self, pdb_file, start_bp, end_bp, nstructs, email=""):
        pass


    @cherrypy.expose
    def design_primers(self, pdb_file, start_bp, end_bp, nstructs, email=""):

        job_dir = os.urandom(16).encode('hex')
        new_dir = "data/"+job_dir
        os.mkdir(new_dir)

        f = open(new_dir + "/rna.pdb", "w")
        while True:
            data = pdb_file.file.read(8192)
            f.write(data)
            if not data:
                break

        f.close()

        f = open("jobs.dat","a")
        f.write(new_dir + " " + nstructs + " " + email + "\n")
        f.close()

        raise cherrypy.HTTPRedirect('/result/' + job_dir)

    @cherrypy.expose
    def result(self, job_id):
        df = pd.read_csv("data/"+ job_id + "/default.scores")

        imgs = glob.glob("data/" + job_id + "/design_*")
        d_imgs = []
        for i, img in enumerate(imgs):
            d_imgs.append(DesignImage("/"+img, "Design " + str(i)))

        results = j2_env.get_template("res/templates/results.html")
        return results.render(
            job_id = job_id,
            d_imgs = d_imgs,
            js_score_plot= get_js_score_plot(df),
            js_length_plot = get_js_length_plot(df),
            js_eterna_score = get_js_eterna_score(df),
            design_infos = get_design_infos(df, job_id)
        )

    @cherrypy.expose
    def old_result(self, dir_id):
        # job not done show waiting page
        path = DATA_BASE_DIR + dir_id + "/weblogo.png"
        error = DATA_BASE_DIR + dir_id + "/ERROR"
        if not os.path.isfile(path) or os.path.isfile(error):
            page = ResultsWaitingPage()
            percent = page.render(dir_id)
            return page.to_str()

        # job is done show results
        all_path =  DATA_BASE_DIR + dir_id + "/all.zip"

        s = get_html_head()
        s += " <script type=\"text/javascript\">\nwindow.onload = function () {\n"
        recovery_file = "data/" + dir_id + "/rna_RNA.sequence_recovery.txt"
        summary_file = "data/" + dir_id + "/summary.txt"
        score_file = "data/" + dir_id + "/rna_RNA.pack.out"
        sequence_file = "data/" + dir_id + "/rna_RNA.pack.txt"
        s += get_js_native_recovery_chart(recovery_file)
        s += get_js_energy_vs_sequence_identity(summary_file)
        s += "}\n</script></head>"
        s += "<body>\n"
        s += get_nav_bar()
        s += "<center><H2>Job "+dir_id + " Results </H2></center>"
        s += """<div class=\"starter-template\">
         <div class=\"container theme-showcase\" role=\"main\">"""

        #s += "<a href=/download/?filepath=%s><button type=\"button\" \
        #      class=\"btn btn-primary\">Download Everything</button></a>" % (all_path)
        s += "<a href=/download/?dir_id=%s&data=all><button type=\"button\" \
              class=\"btn btn-primary\">Download Everything</button></a>" % (dir_id)
        s += "<br><br><br>"

        s += get_cluster_table(dir_id)
        s += "<br /><br />"
        s += "<img src=/data/"+dir_id+"/weblogo.png />"
        s += "<div id=\"NativeRecovery\" style=\"height: 300px; width: 100%; \"></div>"
        s += "<div id=\"EnergyScatter\" style=\"height: 300px; width: 100%; \"></div>"
        s += "</body></html>"

        return s


class Download:

    def index(self, dir_id, data):
        filepath =  DATA_BASE_DIR + dir_id + "/all.zip"
        return serve_file(filepath, "application/x-download", "attachment")
    index.exposed = True


if __name__ == "__main__":
    #n = navbar.NavBarHeader("RNA Redesign", link="/res/html/Design.html")
    #print n.body

    #exit()

    server_state = "development"
    if len(sys.argv) > 1:
        server_state = sys.argv[1]
    if server_state not in ("development","release"):
        raise SystemError("ERROR: Only can do development or release")
    if server_state == "development":
        socket_host = "127.0.0.1"
        socket_port = 8080
    else:
        socket_host = "0.0.0.0"
        #socket_host = "52.10.248.184"
        socket_port = 8080

    cherrypy.config.update( {
        "server.socket_host":socket_host,
        "server.socket_port":socket_port,
        "tools.staticdir.root": os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
    } )
    root = rest()
    root.download = Download()

    if server_state == "development":
        cherrypy.quickstart(root, "", "test.conf")
    else:
        cherrypy.quickstart(root, "", "app.conf")


