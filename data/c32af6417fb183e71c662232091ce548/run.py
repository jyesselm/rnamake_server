import subprocess

for i in range(10):
    subprocess.call("/Applications/MacPyMOL.app/Contents/MacOS/MacPyMOL -pc design." + \
                    str(i) + ".pdb -d \" rc(); orient; set ray_opaque_background, off; ray 320, 240; png test.png; quit\"",
                    shell=True)
    subprocess.call("convert test.png -trim design_" + str(i) + ".png",
                    shell=True)