# Project-Zomboid-Scripts

Useful tools I made for maintaining my project zomboid dedicated server

## InstallMods.py

Adds a list of mods from a Steam workshop collection to the servertest.ini file. 
Requires Python version 3 and beautifulsoup4 library installed. Must be placed within the server directory: `Zomboid/Server/`. Server must have been run at least once before.

To Install beautifulsoup4 run this command line:
```
python3 -m pip install beautifulsoup4 requests
```
