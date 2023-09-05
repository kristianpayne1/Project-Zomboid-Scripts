import concurrent.futures
from typing import List

import requests
import argparse
from bs4 import BeautifulSoup
from pathlib import Path
import re
import time


WORKSHOP_CONFIG_KEY = "WorkshopItems"
MODS_CONFIG_KEY = "Mods"
STEAM_WORKSHOP_TEMPLATE_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=%s"


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_mod_ids(workshop_id: str):
    # For workshop item, find the mod ID
    mod_html = requests.get(STEAM_WORKSHOP_TEMPLATE_URL % workshop_id).text
    mod_soup = BeautifulSoup(mod_html, "html.parser")
    mod_page_text = mod_soup.get_text()
    if "Mod ID:" in mod_page_text or "ModID:" in mod_page_text:
        modIDs = re.findall(r'(?:(?<=Mod ID: )|(?<=ModID: ))(.*?)(?=\W)', mod_page_text)
        for modID in modIDs:
            print(modID)
        return modIDs
    else:
        print(BColors.FAIL + "Couldn't find Mod ID for workshop item: {}".format(workshop_id) + BColors.ENDC)
        return []


def replace_key_or_add(key: str, replacement: str, s: str) -> str:
    if key not in s:
        return s + '\n' + replacement

    pattern = f"\b{key}[^\b]*\b"
    return re.sub(pattern, replacement, s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Project Zomboid mod installer")
    parser.add_argument("url", type=str, help="Steam collection URL")
    parser.add_argument("--server-file", type=Path, default=Path("./servertest.ini"), help="Path to servertest.ini (or server's ini config file)")
    parser.add_argument('-p', "--print-only", default=False, action="store_const", const=True, help="Don't write to server config file and print mod IDs instead")

    args = parser.parse_args()

    print_only: bool = args.print_only

    collection_url: str = args.url
    if collection_url == "":
        print(BColors.FAIL + "Collection URL empty! Please the collection URL" + BColors.ENDC)
        exit()

    server_config: Path = args.server_file.expanduser().absolute()
    if not server_config.exists() and not print_only:
        print(BColors.FAIL + f"No {server_config} file found! Make sure you have started your server at least once before and specified the path to the config" + BColors.ENDC)
        exit()

    print(BColors.HEADER + "========== Overwriting mod list ==========" + BColors.ENDC)

    # Read collection HTML
    collectionHTML = requests.get(collection_url).text
    collectionSoup = BeautifulSoup(collectionHTML, "html.parser")

    # Find items
    collectionItems = collectionSoup.find_all("div", "collectionItem")

    print(f"{len(collectionItems)} workshop items found:")

    # Extract IDs and format to semi-colon seperated string
    workshopIDs = []
    for item in collectionItems:
        id = item["id"].split("_")[1]
        if id:
            workshopIDs.append(id)

    formattedWorkshopIDs = ';'.join(workshopIDs)
    workshop_line = f"{WORKSHOP_CONFIG_KEY}={formattedWorkshopIDs}"

    # Multi-threading go zoom 🏎️💨
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(get_mod_ids, workshopIDs)

    modIDs = [item for sublist in list(results) for item in sublist]
    formattedModIDs = ';'.join(modIDs)
    mods_line = f"{MODS_CONFIG_KEY}={formattedModIDs}"

    print()

    if print_only:
        print(f"Workshop IDs: {formattedWorkshopIDs}")
        print(f"Mod IDs: {formattedModIDs}")
        exit()

    # Write to servertest.ini
    with server_config.open('r+') as file:
        file_string: str = file.read()

    file_string = replace_key_or_add(WORKSHOP_CONFIG_KEY, workshop_line, file_string)
    file_string = replace_key_or_add(MODS_CONFIG_KEY, mods_line, file_string)

    with server_config.open('w') as file:
        file.write(file_string)

    print(BColors.OKGREEN + f"Finished writing to {server_config} ✅" + BColors.ENDC)
    print(BColors.HEADER + "=========================================" + BColors.ENDC)
