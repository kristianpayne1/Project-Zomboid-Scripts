import os
from pathlib import Path
from scripts.InstallMods import main

STEAM_URL = os.environ['STEAM_URL']

def test_main():
    main(STEAM_URL, Path("./test/servertest.ini"))