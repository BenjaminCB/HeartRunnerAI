import geojson
import itertools
import csv
from geojson_length import calculate_distance, Unit


STREETS_GEOJSON_PATH = "./geojson/streetsegments.geojson"
AEDS_GEOJSON_PATH = "./geojson/aeds.geojson"
STREETS_PATH = "./csv/streetsegments.csv"
AEDS_PATH = "./csv/aeds.csv"
INTERS_PATH = "./csv/intersections.csv"
AED_LOCATIONS_PATH = "./csv/aed_locations.csv"
STREETS_HEADER = ["ID", "HEAD_INTERSECTION_ID",
                  "TAIL_INTERSECTION_ID", "LENGTH"]
INTERS_HEADER = ["ID", "X_COORD", "Y_COORD"]
AEDS_HEADER = ["ID", "X_COORD", "Y_COORD"]
AED_LOCATIONS_HEADER = ["AED_ID", "INTERSECTION_ID"]


class Intersection:
    id_iter = itertools.count(1)

    def __init__(self, coord):
        self.id = next(self.id_iter)
        self.xcoord, self.ycoord = coord
        self.csv = [self.id, self.xcoord, self.ycoord]


class StreetSegment:
    def __init__(self, id, head_id, tail_id, length):
        self.id = id
        self.head_intersection_id = head_id
        self.tail_intersection_id = tail_id
        self.length = length
        self.csv = [self.id, self.head_intersection_id,
                    self.tail_intersection_id, self.length]


class Aed:
    def __init__(self, id, coord):
        self.id = id
        self.xcoord, self.ycoord = coord
        self.csv = [self.id, self.xcoord, self.ycoord]


class AedLocation:
    def __init__(self, aed_id, intersection_id):
        self.aed_id = aed_id
        self.intersection_id = intersection_id
        self.csv = [self.aed_id, self.intersection_id]


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
    open(STREETS_GEOJSON_PATH, "r") as streets_geojson_file,
    open(AEDS_GEOJSON_PATH, "r") as aeds_geojson_file,
    open(STREETS_PATH, "w+", encoding='UTF8', newline='') as streets_file,
    open(INTERS_PATH, "w+", encoding='UTF8', newline='') as inters_file,
    open(AEDS_PATH, "w+", encoding='UTF8', newline='') as aeds_file,
    open(AED_LOCATIONS_PATH, "w+", encoding='UTF8', newline='') as aed_locations_file
):
    inters = {}
    streets_writer = csv.writer(streets_file)
    inters_writer = csv.writer(inters_file)
    aeds_writer = csv.writer(aeds_file)
    aed_locations_writer = csv.writer(aed_locations_file)

    streets_writer.writerow(STREETS_HEADER)
    inters_writer.writerow(INTERS_HEADER)
    aeds_writer.writerow(AEDS_HEADER)
    aed_locations_writer.writerow(AED_LOCATIONS_HEADER)

    print(f"Generating {STREETS_PATH} and {INTERS_PATH} datasets")
    street_features = geojson.load(streets_geojson_file)["features"]
    for feature in street_features:
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

    print(f"DONE!")

    print(f"Generating {AEDS_PATH} and {AED_LOCATIONS_PATH} dataset")
    aed_features = geojson.load(aeds_geojson_file)["features"]
    for feature in aed_features:
        id = feature["properties"]["OBJECTID"]
        coords = tuple(feature["geometry"]["coordinates"])
        aeds_writer.writerow(Aed(id, coords).csv)

        if coords not in inters:
            inters[coords] = Intersection(coords)
            inters_writer.writerow(inters[coords].csv)

        aed_locations_writer.writerow(AedLocation(id, inters[coords].id).csv)

    print(f"DONE!")
