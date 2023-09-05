import os
import sys

from pathlib import Path
from scripts.install_mods.install_mods import main

sys.path.insert(0, '.')

STEAM_URL = os.environ['STEAM_URL']

def test_main():
    main(STEAM_URL, Path("./test/servertest.ini"))