import subprocess


def render_pdb_to_png_mac(path, name):
    subprocess.call(
        "/Applications/MacPyMOL.app/Contents/MacOS/MacPyMOL -pc " + \
        path + " -d \" rc(); orient; set ray_opaque_background, off; " +
        "ray 640, 480; png test.png; quit\"",
        shell=True)

    subprocess.call(
        "convert test.png -trim " + name,
        shell=True)


def render_pdb_to_png(path, name):
    subprocess.call(
        "pymol -pc " + \
        path + " -d \" rc(); orient; set ray_opaque_background, off; " +
        "ray 640, 480; png test.png; quit\"",
        shell=True)

    subprocess.call(
        "convert test.png -trim " + name,
        shell=True)