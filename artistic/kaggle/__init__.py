from pathlib import Path
import subprocess

from artistic.kaggle.blur import blur
from artistic.kaggle.nst import nst
from artistic.kaggle.palette import palette
from artistic.kaggle.transfer_color import transfer_color

ROOT = Path(__file__).parent.parent


def run(filename):
    subprocess.run([f'kaggle kernels push -p {ROOT.joinpath("temp")}/'], shell=True)
    Path(ROOT.joinpath(f'temp/{filename}')).unlink(missing_ok=True)
    Path(ROOT.joinpath('temp/kernel-metadata.json')).unlink(missing_ok=True)
