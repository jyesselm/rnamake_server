import subprocess


def render_pdb_to_png_mac(path):
    subprocess.call(
        "/Applications/MacPyMOL.app/Contents/MacOS/MacPyMOL -pc " + \
        path + " -d \" rc(); orient; set ray_opaque_background, off; " +
        "ray 640, 480; png test.png; quit\"",
        shell=True)

    subprocess.call(
        "convert test.png -trim " + path[:-4] + ".png",
        shell=True)