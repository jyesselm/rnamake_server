import glob
import os
import shutil

dirs = glob.glob("data/*")

for d in dirs:
    if os.path.isfile(d + "/scaffold.png"):
        shutil.copy(d + "/scaffold.png", d + "/input.png")