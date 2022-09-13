from urllib.request import urlopen
from bs4 import BeautifulSoup
from pathlib import Path
from threading import Thread
import re
import time


class WebWorker(Thread):
    # Worker to crawl workshop page and find modID
    def __init__(self, workshopIDs):
        Thread.__init__(self)
        self.workshopIDs = workshopIDs

    def run(self):
        # For each workshop item, find the mod ID
        for id in self.workshopIDs:
            modPage = urlopen(
                "https://steamcommunity.com/sharedfiles/filedetails/?id={0}".format(id))
            modHTML = modPage.read().decode("utf-8")
            modSoup = BeautifulSoup(modHTML, "html.parser")
            modPageText = modSoup.get_text()
            if "Mod ID:" in modPageText:
                modID = re.findall("(?<=Mod ID: )(.*)(?=\s)", modPageText)[0]
                if modID:
                    print(modID)
                    modIDs.append(modID)


print("========== Overwriting mod list ==========")
start = time.time()

# URL of workshop collection
url = "https://steamcommunity.com/sharedfiles/filedetails/?id=2861142922"

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

# Multi-threading go better performance
numThreads = 1  # for some reason only 1 thread is fastest.
threads = []
modIDs = []

# Start new Threads
for i in range(0, len(workshopIDs), numThreads):
    worker = WebWorker(workshopIDs[i:i + numThreads])
    threads.append(worker)
    worker.start()

for t in threads:
    t.join()

formattedModIDs = ';'.join(modIDs)
print()

# Write to servertest.ini
p = Path(__file__).with_name('servertest.ini')
with p.open('r') as f:
    data = f.readlines()

workshopIDIndex = [i for i, s in enumerate(data) if 'WorkshopItems=' in s][1]
data[workshopIDIndex] = "WorkshopItems={}\n".format(formattedWorkshopIDs)
print(data[workshopIDIndex])

modIDIndex = [i for i, s in enumerate(data) if 'Mods=' in s][0]
data[modIDIndex] = "Mods={}\n".format(formattedModIDs)
print(data[modIDIndex])

with p.open('w') as f:
    f.writelines(data)

print("Finished writing to servertest.ini ✅")
end = time.time()
print(end-start)
print("=========================================")
