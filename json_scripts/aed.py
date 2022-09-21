import json

list = []
with open("./AED.json") as file:
    data = json.load(file)
    for feature in data["features"]:
        id = feature["properties"]["OBJECTID"]
        xcoord, ycoord = feature["geometry"]["coordinates"]
        list.append((id, xcoord, ycoord))

for entry in list:
    print(entry)
