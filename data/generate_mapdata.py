import geojson
import itertools
import csv
from geojson_length import calculate_distance, Unit


GEOJSON_PATH = "./geojson/streetsegments.geojson"
STREETS_PATH = "./csv/streetsegments.csv"
INTERS_PATH = "./csv/intersections.csv"
STREETS_HEADER = ["ID", "HEAD_INTERSECTION_ID",
                  "TAIL_INTERSECTION_ID", "LENGTH"]
INTERS_HEADER = ["ID", "X_COORD", "Y_COORD"]


class Intersection:
    id_iter = itertools.count(1)

    def __init__(self, coord):
        self.id = next(self.id_iter)
        self.xcoord = coord[0]
        self.ycoord = coord[1]
        self.csv = [self.id, self.xcoord, self.ycoord]


class StreetSegment:
    def __init__(self, id, head_id, tail_id, length):
        self.id = id
        self.head_intersection_id = head_id
        self.tail_intersection_id = tail_id
        self.length = length
        self.csv = [self.id, self.head_intersection_id,
                    self.tail_intersection_id, self.length]


def filter(feature):
    properties = feature["properties"]
    geometry = feature["geometry"]
    if geometry["type"] not in ["LineString", "MultiLineString"]:
        return True
    if properties["FUNCTIONALCLASS"] in ["Interstate", "Other Freeways & Expressways"]:
        return True
    if properties["ROADTYPE"] in ["Ramp", "ServiceRoad", "Driveway"]:
        return True
    return False


with (
    open(GEOJSON_PATH, "r") as geojson_file,
    open(STREETS_PATH, "w+", encoding='UTF8', newline='') as streets_file,
    open(INTERS_PATH, "w+", encoding='UTF"', newline='') as inters_file
):
    inters = {}
    streets_writer = csv.writer(streets_file)
    inters_writer = csv.writer(inters_file)

    streets_writer.writerow(STREETS_HEADER)
    inters_writer.writerow(INTERS_HEADER)

    n = 1
    features = geojson.load(geojson_file)["features"]
    for feature in features:
        print(n/len(features)*100)
        n += 1

        # Filter unwanted features.
        if filter(feature):
            continue

        # Calculate the length and get the id of the streetsegment
        length = calculate_distance(feature, Unit.meters)
        id = feature["properties"]["OBJECTID"]

        # Check if an intersection exists for the first and last coordinate of the
        # streetsegment, if not create a new intersection at those coordinates.
        coords = list(geojson.coords(feature))
        first_coord = coords[0]
        last_coord = coords[-1]
        if first_coord == last_coord:
            continue
        if first_coord not in inters:
            inters[first_coord] = Intersection(first_coord)
            inters_writer.writerow(inters[first_coord].csv)
        if last_coord not in inters:
            inters[last_coord] = Intersection(last_coord)
            inters_writer.writerow(inters[last_coord].csv)

        streets_writer.writerow(StreetSegment(
            id, inters[first_coord].id, inters[last_coord].id, length).csv)
