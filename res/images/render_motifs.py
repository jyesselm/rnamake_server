import subprocess
import glob
import os

motif_dirs = glob.glob("/Users/jyesselm/projects/RNAMake/rnamake/resources/motifs/two_ways/*")

for d in motif_dirs:
    if not os.path.isdir(d):
        continue
    spl = d.split("/")
    pdb_file = d + "/" + spl[-1] + ".pdb"
    subprocess.call("/Applications/MacPyMOL.app/Contents/MacOS/MacPyMOL -pc " + \
                    pdb_file + " -d \" rr(); orient; set ray_opaque_background, off; ray 320, 240; png test.png; quit\"",
                    shell=True)
    subprocess.call("convert test.png -trim motifs/" + spl[-1] + ".png",
                    shell=True)
