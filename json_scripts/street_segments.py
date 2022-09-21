import json
import math
from geojson_length import calculate_distance, Unit
from geojson import Feature, LineString, MultiLineString

coordinates = [ [ -77.003989132433176, 38.921307128966255 ], [ -77.003617223236617, 38.921307495103797 ], [ -77.003603385269088, 38.921307495531543 ], [ -77.003503636572916, 38.921307228316763 ] ]
line = Feature(geometry=LineString(coordinates))

def sum(arr):
    res = 0
    for x in arr:
        res += x
    return res;


list = []
with open("./StreetSegments.json") as file:
    data = json.load(file)
    for feature in data["features"]:
        if feature["geometry"]["type"] == "MultiLineString":
            line_length = lambda coords: calculate_distance(Feature(geometry=LineString(coords)), Unit.meters)
            length = sum(map(line_length, feature["geometry"]["coordinates"]))
        elif feature["geometry"]["type"] == "LineString":
            f = Feature(geometry=LineString(feature["geometry"]["coordinates"]))
            length = calculate_distance(f, Unit.meters)
        else:
            continue
        list.append(length)

for entry in list:
    print(entry)
