import os
import platform

file_path = os.path.realpath(__file__)
spl = file_path.split("/")
BASE_DIR = "/".join(spl[:-1])
TOP_DIR = "/".join(spl[:-2])
DATA_DIR = TOP_DIR + "/data/"
RES_DIR = TOP_DIR + "/res/"
TEMPLATES_DIR = BASE_DIR + "/templates/"
UNITTEST_DIR = BASE_DIR + "/unittests/"

OS = None
if platform.system() == 'Linux':
    OS = 'linux'
elif platform.system() == 'Darwin':
    OS = 'osx'
else:
    raise SystemError(platform.system() + " is not supported currently")