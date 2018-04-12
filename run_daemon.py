import time
import sys
import subprocess
import shutil
import os
import zipfile
import argparse
import threading
import glob

#import rna_design.email_client
from rnamake_server import job_queue, tools

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-mode', help='what mode is the daemon being run in', required=True)
    parser.add_argument('-job', help='what mode is the daemon being run in', required=False)

    args = parser.parse_args()
    return args


def get_top_clusters():
    # TODO check for max number to format pdb num
    f = open("rna_RNA.sequence_recovery.txt")
    lines = f.readlines()
    f.close()

    native = ""
    for l in lines:
        spl = l.split()
        if len(spl) < 2:
            break
        native += spl[0]

    f = open("rna_RNA.pack.txt")
    lines = f.readlines()
    f.close()

    clusters = []
    f = open('summary.txt', 'w')
    f.write("model  rosetta energy  sequence  % sequence recovery\n")
    for i,l in enumerate(lines):
        spl = l.split()
        same = 0.0
        for j in range(len(spl[1])):
            if native[j] == spl[1][j]:
                same += 1
        percent = (same / float(len(native)))*100

        f.write(format_pdb_num(i+1) + " " + spl[0] + " " + spl[1] + " " + str(percent) + "\n")
    f.close()

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
        if server_state == "release":
            subprocess.call("pymol -pc "+\
                             c.pdb_file + " -d \" rr(); ray 320, 240; png test.png; quit\"",
                             shell=True)
        else:
            subprocess.call("/Applications/MacPyMOL.app/Contents/MacOS/MacPyMOL -pc "+\
                             c.pdb_file + " -d \" rr(); ray 320, 240; png test.png; quit\"",
                             shell=True)


        subprocess.call("convert test.png -trim cluster_" + str(i) + ".png",
                        shell=True)


    shutil.copy('../../output_README', 'README')

    f = zipfile.ZipFile("all.zip", "w")
    for name in os.listdir('.'):
        if name[-4:] != '.pdb' or name[:3] == 'rna':
            continue
        f.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    f.write("summary.txt", os.path.basename("summary.txt"), zipfile.ZIP_DEFLATED)
    f.write("README",  os.path.basename("README"), zipfile.ZIP_DEFLATED)
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



class ScaffoldDesignJob(threading.Thread):
    def __init__(self, mode, j):
        threading.Thread.__init__(self)
        self.mode = mode
        self.success =0
        self.j = j

    def run(self):
        #TODO add errors for improper pdb formats
        os.chdir("data/"+self.j.id)
        subprocess.call("design_rna -pdb scaffold.pdb"
                        " -start_bp %s -end_bp %s -designs %s -pdbs " %
                        (self.j.args['start_bp'], self.j.args['end_bp'], self.j.args['nstruct']),
                        shell=True)

        pdb_files = glob.glob("design.*.pdb")
        if len(pdb_files) == 0:
            f = open("ERRORS", "w")
            f.write("No solutions were found. Sorry :(. Please see FAQ for what to do")
            f.close()
            return

        if self.mode == "devel":
            for pdb_file in pdb_files:
                tools.render_pdb_to_png_mac(pdb_file)
        else:
            raise ValueError("mode: " + self.mode  + " is not supported ")

        self.success = 1

    def join(self):
        threading.Thread.join(self)
        return self.success


class RNAMakeDaemon(object):
    def __init__(self, mode):
        self.mode = mode
        self.job_queue = job_queue.JobQueue()
        self.job_runner = None

    def run(self):
        print "starting daemon"
        while True:
            print "waiting for jobs"

            if self.job_queue.has_queued_jobs():
                j = self.job_queue.get_next_queued_job()
                self.run_job(j.id)

            time.sleep(60)


    def run_job(self, job_id):
        j = self.job_queue.get_job(job_id)
        if j is None:
            raise ValueError(job_id + " is a unknown job id")

        if j.type == job_queue.JobType.SCAFFOLD:
            self.job_runner = ScaffoldDesignJob(self.mode, j)
            self.job_runner.start()

        total_time = 10
        print job_id + " has started"
        while self.job_runner.is_alive():
            time.sleep(10)
            print job_id + " has been running for " + str(total_time) + " seconds"
            total_time += 10

        success = self.job_runner.join()
        if success:
            print job_id + " completed successfully!"
            self.job_queue.update_job_status(job_id, job_queue.JobStatus.FINISHED)
        else:
            print job_id + " completed with an error!"
            self.job_queue.update_job_status(job_id, job_queue.JobStatus.ERROR)



if __name__ == "__main__":
    args = parse_args()
    d = RNAMakeDaemon(args.mode)

    if args.job:
        d.run_job(args.job)
    else:
        d.run()

    exit()





exit()


server_state = "development"
if len(sys.argv) > 1:
    server_state = sys.argv[1]
if server_state not in ("development","release"):
    raise SystemError("ERROR: Only can do development or release")

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

    get_top_clusters()
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

