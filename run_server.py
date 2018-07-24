import cherrypy
import pandas as pd
from cherrypy.lib.static import serve_file
from jinja2 import Environment, FileSystemLoader

import os
import string
import sys
import glob
import json
import argparse

from collections import namedtuple

from rnamake import resource_manager as rm

from rnamake_server import job_queue, tools


DesignImage = namedtuple('DesignImage', ['path', 'name'])
DesignInfo = namedtuple('DesignInfo', ['img_path', 'design_num', 'score',
                                       'eterna_score', 'sequence', 'structure', 'motifs_used'])
MotifInfo = namedtuple('MotifInfo', ['name', 'num'])


MEDIA_DIR = os.path.join(os.path.abspath("."))
DATA_BASE_DIR = MEDIA_DIR + "/data/"

j2_env = Environment(loader=FileSystemLoader(MEDIA_DIR),
                     trim_blocks=True)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-mode', help='what mode is the server being run in', required=True,
                        choices=['devel', 'release'], type=str)
    parser.add_argument('-no_job_creation', required=False, action="store_true")

    args = parser.parse_args()

    return args


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
        motif_uses = []
        spl = row.motifs_uses.split(";")
        for e in spl[:-1]:
            if e[0] != "T":
                continue
            motif_uses.append(MotifInfo(e, count))
            count += 1

        design_infos.append(
            DesignInfo("/data/"+job_id+"/design."+str(row.design_num)+".png",
                       row.design_num,
                       row.opt_score,
                       row.eterna_score,
                       row.opt_sequence,
                       row.design_structure,
                       motif_uses))
    return design_infos


class RNAMakeServer:
    def __init__(self, mode, no_job_creation):
        self.mode = mode
        self.job_queue = job_queue.JobQueue()
        self.no_job_creation = no_job_creation
        self.design_scaffold_error = ''
        self.atp_stablization_error = ''


    @cherrypy.expose
    def index(self):
        index =  j2_env.get_template("res/templates/index.html")
        return index.render()

    @cherrypy.expose
    def about(self):
        about = j2_env.get_template("res/templates/about.html")
        return about.render()

    @cherrypy.expose
    def design_scaffold_app(self):
        app = j2_env.get_template("/res/templates/design_scaffold.html")
        error = self.design_scaffold_error
        self.design_scaffold_error = ''
        return app.render(
            error=error
        )

    # helper functions
    def setup_job_dir(self, pdb_file, pdb_name, page):
        job_dir = os.urandom(16).encode('hex')
        new_dir = "data/" + job_dir
        os.mkdir(new_dir)

        pdb_path = new_dir + "/" + pdb_name +".pdb"
        f = open(pdb_path, "w")
        while True:
            data = pdb_file.file.read(8192)
            f.write(data)
            if not data:
                break
        f.close()

        self._remove_hetatoms(pdb_path, page)

        if self.mode == "devel":
            tools.render_pdb_to_png_mac(new_dir + "/" + pdb_name +".pdb",
                                        new_dir +  "/input.png")
        else:
            tools.render_pdb_to_png(new_dir + "/" + pdb_name +".pdb",
                                    new_dir + "/input.png")

        return job_dir

    def _remove_hetatoms(self, pdb_path, page):
        f = open(pdb_path)
        lines = f.readlines()
        f.close()

        count = 0
        f = open(pdb_path, "w")
        for l in lines:
            startswith = l[0:6]
            if startswith == 'HETATM':
                continue
            if startswith == 'ATOM  ':
                count += 1
            f.write(l)

        if count == 0:
            self.design_scaffold_error = "alert(\"not a valid PDB\");"
            raise cherrypy.HTTPRedirect('/'+page)

        f.close()


    # validate scaffold pdb
    def _load_structure(self, job_id, pdb):
        try:
            m = rm.manager.get_structure("data/"+job_id+"/"+pdb, pdb[:-4])
        except:
            return None, "not a valid PDB"

        if len(m.residues()) > 100:
            return None, "RNA is too large for server, must be under 100 residues." \
                         " Please download RNAMake and run locally for larger jobs."

        return m, None

    def _check_basepair_ends_exist(self, m, start_bp, end_bp):
        bps = [start_bp, end_bp]
        # do residues exist?
        for bp in bps:
            spl = bp.split("-")
            r = m.get_residue(num=int(spl[0][1:]), chain_id=spl[0][0])
            if r is None:
                return "residue: "+spl[0]+" does not exist in supplied pdb, it is " +\
                       "parsed to have chain id: " + spl[0][0] + " and residue number: " +\
                       spl[0][1:]

            r = m.get_residue(num=int(spl[1][1:]), chain_id=spl[1][0])
            if r is None:
                return "residue: "+spl[1]+" does not exist in supplied pdb, it is " +\
                       "parsed to have chain id: " + spl[1][0] + " and residue number: " +\
                       spl[1][1:]

        for bp_name in bps:
            bp = m.get_basepair(name=bp_name)
            spl = bp_name.split("-")
            bp_reverse_name = spl[1] + "-" + spl[0]
            bp_reverse = m.get_basepair(name=bp_reverse_name)

            if len(bp) == 0 and len(bp_reverse) == 0:
                return "basepair: " + bp_name + " does not exist! both residues exist but no" +\
                       " basepair between them!"

            # user submitted the name backwards
            if len(bp) == 0 and len(bp_reverse) != 0:
                bp_name = bp_reverse_name

            try:
                end = m.get_end_index(name=bp_name)
            except:
                return "basepair: " + bp_name + " exists but it is not a basepair end " +\
                       " which is defined by an base pair with residues that are both at the " +\
                       " end of RNA chains, are Watson-Crick and contain a 5' and 3' residue"


        return None

    @cherrypy.expose
    def design_scaffold(self, pdb_file, start_bp, end_bp, nstruct, email=""):
        job_id = self.setup_job_dir(pdb_file, "input", "design_scaffold_app")

        args = {
            'nstruct': nstruct,
            'start_bp': start_bp,
            'end_bp': end_bp
        }

        m, error = self._load_structure(job_id, "input.pdb")
        if error is not None:
            self.design_scaffold_error = "alert(\"" + error + "\");"
            raise cherrypy.HTTPRedirect('/design_scaffold_app')

        error = self._check_basepair_ends_exist(m, start_bp, end_bp)
        if error is not None:
            print error
            self.design_scaffold_error = "alert(\"" + error + "\");"
            raise cherrypy.HTTPRedirect('/design_scaffold_app')

        if not self.no_job_creation:
            self.job_queue.add_job(job_id, job_queue.JobType.SCAFFOLD, json.dumps(args),
                                   email=email)
            cherrypy.log("created new job: " + job_id)
            raise cherrypy.HTTPRedirect('/result/' + job_id)
        else:
            raise cherrypy.HTTPRedirect('/design_scaffold_app')

    @cherrypy.expose
    def apt_stablization_app(self):
        app = j2_env.get_template("/res/templates/apt_stablization.html")
        error = self.atp_stablization_error
        self.atp_stablization_error = ''
        return app.render(
            error=error
        )

    @cherrypy.expose
    def apt_stablization(self, pdb_file, nstruct, email=""):
        job_id = self.setup_job_dir(pdb_file, "input", "apt_stablization_app")

        m, error = self._load_structure(job_id, "input.pdb")
        if error is not None:
            self.atp_stablization_error = "alert(\"" + error + "\");"
            raise cherrypy.HTTPRedirect('/apt_stablization_app')

        args = {
            'nstruct': nstruct
        }

        if not self.no_job_creation:
            self.job_queue.add_job(job_id, job_queue.JobType.APT_STABLIZATION, json.dumps(args),
                                   email=email)
            cherrypy.log("created new job: " + job_id)
            raise cherrypy.HTTPRedirect('/result/' + job_id)
        else:
            raise cherrypy.HTTPRedirect('/apt_stablization_app')

    @cherrypy.expose
    def result(self, job_id):
        # unknown job id folder
        if not os.path.isdir("data/" + job_id):
            print "made it"
            app = j2_env.get_template("/res/templates/unknown_result.html")
            return app.render(
                job_id = job_id)

        j = self.job_queue.get_job(job_id)

        # second check maybe deleted job?
        if j is None:
            app = j2_env.get_template("/res/templates/unknown_result.html")
            return app.render(
                job_id=job_id)

        # job not completed
        if j.status == job_queue.JobStatus.QUEUED:
            app = j2_env.get_template("/res/templates/result_status.html")
            return app.render(
                j = j)


        df = pd.read_csv("data/"+ job_id + "/default.scores")
        results = j2_env.get_template("res/templates/results.html")
        return results.render(
            j = j,
            js_score_plot= get_js_score_plot(df),
            js_length_plot = get_js_length_plot(df),
            js_eterna_score = get_js_eterna_score(df),
            design_infos = get_design_infos(df, job_id)
        )

    @cherrypy.expose
    def download(self, f_path):
        spl = f_path.split("/")
        if spl[0] != "data":
            raise cherrypy.HTTPError(401, 'Unauthorized')

        filepath =  os.path.abspath(f_path)
        return serve_file(filepath, "application/x-download", "attachment")


if __name__ == "__main__":
    args = parse_args()


    server_state = args.mode
    if server_state == "devel":
        socket_host = "127.0.0.1"
        socket_port = 8080
    else:
        socket_host = "0.0.0.0"
        socket_port = 8080

    cherrypy.config.update( {
        "server.socket_host":socket_host,
        "server.socket_port":socket_port,
        "tools.staticdir.root": os.path.abspath(os.path.join(os.path.dirname(__file__), "")),
        "server.thread_pool": 100
    } )
    root = RNAMakeServer(server_state, args.no_job_creation)

    if server_state == "devel":
        cherrypy.quickstart(root, "", "test.conf")
    else:
        cherrypy.quickstart(root, "", "app.conf")





























