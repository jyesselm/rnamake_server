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
import job_queue, tools, settings

class ScaffoldDesignJob(threading.Thread):
    def __init__(self, mode, j):
        threading.Thread.__init__(self)
        self.mode = mode
        self.success =0
        self.j = j

    def run(self):
        os.chdir("data/"+self.j.id)
        subprocess.call("design_rna -pdb input.pdb"
                        " -start_bp %s -end_bp %s -designs %s -pdbs " %
                        (self.j.args['start_bp'], self.j.args['end_bp'], self.j.args['nstruct']),
                        shell=True)

        pdb_files = glob.glob("design.*.pdb")
        if len(pdb_files) == 0:
            f = open("ERRORS", "w")
            f.write("No solutions were found. Sorry :(. Please see FAQ for what to do")
            f.close()
            os.chdir(settings.TOP_DIR)
            return

        if self.mode == "devel":
            for pdb_file in pdb_files:
                tools.render_pdb_to_png_mac(pdb_file, pdb_file[:-4]+".png")
        elif self.mode == "release":
            for pdb_file in pdb_files:
                tools.render_pdb_to_png(pdb_file)
        else:
            raise ValueError("mode: " + self.mode  + " is not supported ")

        os.chdir(settings.TOP_DIR)
        self.success = 1

    def join(self):
        threading.Thread.join(self)
        return self.success


class APTStablizationJob(threading.Thread):
    def __init__(self, mode, j):
        threading.Thread.__init__(self)
        self.mode = mode
        self.success = 0
        self.j = j

    def run(self):
        os.chdir("data/"+self.j.id)
        subprocess.call("apt_stablization -pdb aptamer.pdb -designs %s " % (self.j.args['nstruct']) ,
                        shell=True)

        pdb_files = glob.glob("design.*.pdb")
        if len(pdb_files) == 0:
            f = open("ERRORS", "w")
            f.write("No solutions were found. Sorry :(. Please see FAQ for what to do")
            f.close()
            os.chdir(settings.TOP_DIR)
            return

        if self.mode == "devel":
            for pdb_file in pdb_files:
                tools.render_pdb_to_png_mac(pdb_file)
        elif self.mode == "release":
            for pdb_file in pdb_files:
                tools.render_pdb_to_png(pdb_file)
        else:
            raise ValueError("mode: " + self.mode + " is not supported ")

        os.chdir(settings.TOP_DIR)
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

    def _generate_job(self, j):
        if   j.type == job_queue.JobType.SCAFFOLD:
            return ScaffoldDesignJob(self.mode, j)
        elif j.type == job_queue.JobType.APT_STABLIZATION:
            return APTStablizationJob(self.mode, j)
        else:
            raise RuntimeError("unkown job type: " + j.type_str())

    def run_job(self, job_id):
        j = self.job_queue.get_job(job_id)
        if j is None:
            raise ValueError(job_id + " is a unknown job id")

        self.job_runner = self._generate_job(j)
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

