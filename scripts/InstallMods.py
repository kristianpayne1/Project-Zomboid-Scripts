import concurrent.futures
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pathlib import Path
import re
import time
import sys

# URL of workshop collection. ADD URL HERE! i.e https://steamcommunity.com/sharedfiles/filedetails/?id=[collectionID]
url = ""
# Filepath to servertest.ini. Currently assumes in the same directory
serverTestFilePath = Path(__file__).with_name('servertest.ini')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def getModIDs(workshopID):
    # For workshop item, find the mod ID
    modPage = urlopen(
        "https://steamcommunity.com/sharedfiles/filedetails/?id={0}".format(workshopID))
    modHTML = modPage.read().decode("utf-8")
    modSoup = BeautifulSoup(modHTML, "html.parser")
    modPageText = modSoup.get_text()
    if "Mod ID:" in modPageText or "ModID:" in modPageText:
        modIDs = re.findall(
            r'(?:(?<=Mod ID: )|(?<=ModID: ))(.*?)(?=\W)', modPageText)
        for modID in modIDs:
            print(modID)
        return modIDs
    else:
        print(bcolors.FAIL +
              "Couldn't find Mod ID for workshop item: {}".format(workshopID) + bcolors.ENDC)
        return []


if __name__ == "__main__":
    if len(url) == 0:
        sys.exit(
            bcolors.FAIL + "Collection URL empty! Please edit the file and provide the URL" + bcolors.ENDC)

    if serverTestFilePath.is_file() is False:
        sys.exit(
            bcolors.FAIL + "No servertest.ini file found! Make sure you have started your server at least once before and placed this script in the right directory (i.e. Zomboid/Server). " + bcolors.ENDC)

    print(bcolors.HEADER + "========== Overwriting mod list ==========" + bcolors.ENDC)

    # Read collection HTML
    collectionPage = urlopen(url)
    collectionHTML = collectionPage.read().decode("utf-8")
    collectionSoup = BeautifulSoup(collectionHTML, "html.parser")

    # Find items
    collectionItems = collectionSoup.find_all("div", "collectionItem")

    print("{0} workshop items found:".format(
        len(collectionItems)))

    # Extract IDs and format to semi-colon seperated string
    workshopIDs = []
    for item in collectionItems:
        id = item["id"].split("_")[1]
        if id:
            workshopIDs.append(id)

    formattedWorkshopIDs = ';'.join(workshopIDs)

    # Multi-threading go zoom 🏎️💨
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(
            getModIDs, workshopIDs)

    modIDs = [item for sublist in list(results) for item in sublist]
    formattedModIDs = ';'.join(modIDs)
    print()

    # Write to servertest.ini
    with serverTestFilePath.open('r') as file:
        data = file.readlines()

    workshopIDIndex = [i for i, s in enumerate(
        data) if 'WorkshopItems=' in s and not '#' in s][0]
    data[workshopIDIndex] = "WorkshopItems={}\n".format(
        formattedWorkshopIDs)
    print(data[workshopIDIndex])

    modIDIndex = [i for i, s in enumerate(
        data) if 'Mods=' in s and not '#' in s][0]
    data[modIDIndex] = "Mods={}\n".format(formattedModIDs)
    print(data[modIDIndex])

    with serverTestFilePath.open('w') as file:
        file.writelines(data)

    print(bcolors.OKGREEN + "Finished writing to servertest.ini ✅" + bcolors.ENDC)
    print(bcolors.HEADER + "=========================================" + bcolors.ENDC)
