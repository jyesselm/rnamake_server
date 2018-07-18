import time
import subprocess
import os
import zipfile
import rna_design.email_client

def run_redesign(nstructs, level):
    #subprocess.call('rna_design.default.linuxgccrelease -s rna_RNA.pdb -database ~/main/database -nstruct '+str(nstructs) +' -ex1:level ' + str(level) + \
    #                ' -score:weights ~/main/database/scoring/weights/farna/rna_hires.wts -dump -restore_pre_talaris_2013_behavior',
    #                shell=True)
    subprocess.call('rna_design -s rna_RNA.pdb -nstruct '+str(nstructs) +' -ex1:level ' + str(level) + \
                    ' -score:weights /Users/josephyesselman/projects/Rosetta/main/database/scoring/weights/farna/rna_hires.wts -dump -restore_pre_talaris_2013_behavior',
                    shell=True)


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


class SequenceCluster(object):
    def __init__(self, sequence, pdb_file):
        self.sequence, self.pdb_file = sequence , pdb_file


def get_top_clusters():
    # TODO check for max number to format pdb num
    f = open("rna_RNA.pack.txt")
    lines = f.readlines()
    f.close()
    clusters = []
    for i,l in enumerate(lines):
        spl = l.split()
        if len(clusters) == 0:
            clusters.append(SequenceCluster(spl[1], format_pdb_num(i+1)))
            continue

        found = 0
        for c in clusters:
            if spl[1] == c.sequence:
                found = 1
                break

        if not found:
            clusters.append(SequenceCluster(spl[1], format_pdb_num(i+1)))
            if len(clusters) > 4:
                break

    # in case you dont get to 5
    for i,l in enumerate(lines):
        spl = l.split()
        if i == 0:
            continue
        clusters.append(SequenceCluster(spl[1], format_pdb_num(i+1)))
        if len(clusters) > 4:
            break


    for i,c in enumerate(clusters):
        subprocess.call("/Applications/MacPyMOL.app/Contents/MacOS/MacPyMOL -pc "+\
                        c.pdb_file + " -d \" rr(); ray 320, 240; png test.png; quit\"",
                        shell=True)
        subprocess.call("convert test.png -trim cluster_" + str(i) + ".png",
                        shell=True)

    f = zipfile.ZipFile("all.zip", "w")
    for name in os.listdir('.'):
	if name[-4:] != '.pdb':
            continue
        f.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    f.close()




def write_fa_file():
    f = open("rna_RNA.pack.txt")
    lines = f.readlines()
    f.close()

    f = open("sequence.fa", "w")
    for i,l in enumerate(lines):
        spl = l.split()
        f.write("> " + str(i) + "\n")
        f.write(spl[1] + "\n")
    f.close()


def generate_weblogo():
    write_fa_file()
    subprocess.call("weblogo -F png --resolution 600 --color green C 'Cytosine' --color red G 'Guanine' --color orange A 'Ade' --color blue U 'Ura' --errorbars NO < sequence.fa > weblogo.png",shell=True)


def write_error_file(error):
    f = open("ERROR", "w")
    f.write(error + ', an email has been sent to the administrator, please email jyesselm@stanford.edu if you have questions')
    f.close()

def update_jobs_file(lines):
    f = open("jobs.dat", "w")
    for l in lines:
        f.write(l)
    f.close()


fr = open("run_jobs", "a")


while True:


    f = open("jobs.dat")
    lines = f.readlines()
    f.close()

    if len(lines) == 0:
        time.sleep(60)
        continue

    print "job detected!"

    spl = lines[0].split()
    cl = lines.pop(0)

    job_dir = spl[0]
    nstruct = int(spl[1])
    email=None

    if len(spl) > 2:
        email = spl[2].rstrip()
    os.chdir(job_dir)
    try:
        run_redesign(int(nstruct), 4)
    except:
        write_error_file('rna_redesign failed')
        os.chdir("../..")
        update_jobs_file(lines)
        continue

    try:
        get_top_clusters()
    except:
        write_error_file('generating top models failed')
        os.chdir("../..")
        update_jobs_file(lines)
        continue

    try:
        generate_weblogo()
    except:
        write_error_file('generating weblogo failed')
        os.chdir("../..")
        update_jobs_file(lines)
        continue

    os.chdir("../..")
    print "job completed"

    if email is not None:
        rna_design.email_client.send_email(email, job_dir[5:])

    fr.write(cl)
    update_jobs_file(lines)

