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
from rnamake_server import  daemon

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

if __name__ == "__main__":
    args = parse_args()
    d = daemon.RNAMakeDaemon(args.mode)

    if args.job:
        d.run_job(args.job)
    else:
        d.run()

    exit()




