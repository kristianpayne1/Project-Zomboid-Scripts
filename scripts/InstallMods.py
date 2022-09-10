from urllib.request import urlopen
from bs4 import BeautifulSoup
from pathlib import Path

print("========== Overwriting mod list ========== \n")

# URL of workshop collection
url = "https://steamcommunity.com/sharedfiles/filedetails/?id=2861142922"

# Read collection HTML
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

# Find items
collectionItems = soup.find_all("div", "collectionItem")

print("{0} workshop items found".format(
    len(collectionItems)))

# Extract IDs and format to semi-colon seperated string
results = []
for item in collectionItems:
    id = item["id"].split("_")[1]
    results.append(id)

formattedResults = ';'.join(results)

# Write to servertest.ini
p = Path(__file__).with_name('servertest.ini')
with p.open('r') as f:
    data = f.readlines()

index = [i for i, s in enumerate(data) if 'WorkshopItems=' in s][1]
data[index] = "WorkshopItems={}\n".format(formattedResults)
print(data[index])

with p.open('w') as f:
    f.writelines(data)

print("=========================================")
