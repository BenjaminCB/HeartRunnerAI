import geojson
import itertools
import csv
from random import randint
from geopy import distance
from geojson_length import calculate_distance, Unit


STREETS_GEOJSON_PATH = "./geojson/streetsegments.geojson"
AEDS_GEOJSON_PATH = "./geojson/aeds.geojson"
STREETS_PATH = "./csv/streetsegments.csv"
AEDS_PATH = "./csv/aeds.csv"
INTERS_PATH = "./csv/intersections.csv"
STREETS_HEADER = ["ID", "HEAD_INTERSECTION_ID",
                  "TAIL_INTERSECTION_ID", "LENGTH"]
INTERS_HEADER = ["ID", "X_COORD", "Y_COORD"]
AEDS_HEADER = ["ID", "INTERSECTION_ID", "IN_USE", "OPEN_HOUR", "CLOSE_HOUR"]


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
    def __init__(self, id, intersection_id, time_range):
        self.id = id
        self.start_hour, self.close_hour = time_range
        self.intersection_id = intersection_id
        self.csv = [self.id, self.intersection_id, False, self.start_hour, self.close_hour]


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
    open(AEDS_PATH, "w+", encoding='UTF8', newline='') as aeds_file
):
    inters = {}
    streets_writer = csv.writer(streets_file)
    inters_writer = csv.writer(inters_file)
    aeds_writer = csv.writer(aeds_file)

    streets_writer.writerow(STREETS_HEADER)
    inters_writer.writerow(INTERS_HEADER)
    aeds_writer.writerow(AEDS_HEADER)

    street_features = geojson.load(streets_geojson_file)["features"]
    n = 1
    for feature in street_features:
        print(f"Generating {STREETS_PATH} and {INTERS_PATH} datasets: {n/len(street_features)*100}%")
        n += 1
        # Filter unwanted features.
        if filter(feature):
            continue

        # Calculate the length and get the id of the streetsegment
        length = calculate_distance(feature, Unit.meters)
        id = feature["properties"]["OBJECTID"]

        # Check if an intersection exists for the first and last coordinate of the
        # streetsegment, if not create a new intersection at those coordinates.
        aed_coords = list(geojson.coords(feature))
        first_coord = aed_coords[0]
        last_coord = aed_coords[-1]
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

    aed_features = geojson.load(aeds_geojson_file)["features"]
    n = 1
    for feature in aed_features:
        print(f"Generating {AEDS_PATH} dataset: {n/len(aed_features)*100}%")
        n += 1
        id = feature["properties"]["OBJECTID"]
        aed_coords = tuple(feature["geometry"]["coordinates"])
        # TODO: Find closest intersection
        if aed_coords not in inters:
            shortest = 1e6
            for inter_coords in inters.keys():
                diff = distance.distance(aed_coords, inter_coords)
                if diff < shortest:
                    shortest = diff
                    closest_inter = inters[inter_coords]
        else:
            closest_inter = inters[aed_coords]

        random = randint(1, 100)
        if random < 40:     time_range = (0, 2359)
        elif random < 70:   time_range = (900, 1700)
        elif random < 90:   time_range = (600, 2300)
        elif random < 95:   time_range = (300, 1200)
        else:               time_range = (2000, 400)
        
        aeds_writer.writerow(Aed(id, closest_inter.id, time_range).csv)

    print(len(inters))
