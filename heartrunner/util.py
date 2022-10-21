import math
import csv
import geojson
import geojson_length
from geopy.distance import great_circle
from .types import Intersection, Streetsegment, AED
from .pathfinder import Graph

INTERSECTIONS_CSV_HEADER = ["id", "latitude", "longitude"]
INTERSECTIONS_CSV_PATH = "data/csv/intersections.csv"
STREETS_CSV_HEADER = ["id", "head_id", "tail_id", "length", "geometry"]
STREETS_CSV_PATH = "data/csv/streetsegments.csv"
AEDS_CSV_HEADER = ["id", "intersection_id", "in_use", "open_hour", "close_hour"]
AEDS_CSV_PATH = "data/csv/aeds.csv"


def parse_geojson(streets_path, aeds_path):
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

    with(
        open(streets_path, "r") as streets_file,
        open(aeds_path, "r") as aeds_file        
    ):
        graph = Graph()
        intersections = {}
        aed_features = geojson.load(aeds_file)["features"]
        street_features = geojson.load(streets_file)["features"]

        n = 1
        street_count = len(street_features)
        for feature in street_features:
            print(f"Parsing features in {streets_path}: {n}/{street_count}")
            n += 1
            if filter(feature):
                continue

            length = geojson_length.calculate_distance(feature)
            coords = list(geojson.coords(feature))
            head_coords = tuple(reversed(coords[0]))
            tail_coords = tuple(reversed(coords[-1]))

            if head_coords not in intersections:
                intersections[head_coords] = Intersection(coords=head_coords)
            if tail_coords not in intersections:
                intersections[tail_coords] = Intersection(coords=tail_coords)

            head = intersections[head_coords]
            tail = intersections[tail_coords]
            street = Streetsegment(
                head_id=head.id,
                tail_id=tail.id,
                length=length,
                geometry=feature["geometry"]
            )
            graph.add_edge(head, tail, street)

        n = 1
        aed_count = len(aed_features)
        for feature in aed_features:
            print(f"Parsing features in {aeds_path}: {n}/{aed_count}")
            n += 1
            
            aed_coords = tuple(reversed(feature["geometry"]["coordinates"]))
            if aed_coords not in intersections:
                shortest = math.inf
                for inter_coords in intersections:
                    distance = great_circle(aed_coords, inter_coords)
                    if distance < shortest:
                        closest_inter = intersections[inter_coords]
                        shortest = distance
            else:
                closest_inter = intersections[aed_coords]

            aed = AED(
                intersection_id=closest_inter.id
            )
            graph.add_aed(closest_inter, aed)

    graph.remove_subgraphs()

    with(
        open(INTERSECTIONS_CSV_PATH, "w+") as intersections_file,
        open(STREETS_CSV_PATH, "w+") as streets_file,
        open(AEDS_CSV_PATH, "w+") as aeds_file
    ):
        intersections_writer = csv.writer(intersections_file)
        streets_writer = csv.writer(streets_file)
        aeds_writer = csv.writer(aeds_file)

        intersections_writer.writerow(INTERSECTIONS_CSV_HEADER)
        for intersection in graph.nodes.values():
            intersections_writer.writerow([
                intersection.id,
                intersection.latitude,
                intersection.longitude
            ])
        
        streets_writer.writerow(STREETS_CSV_HEADER)
        for street in graph.edges.values():
            streets_writer.writerow([
                street.id,
                street.head_id,
                street.tail_id,
                street.length,
                street.geometry
            ])

        aeds_writer.writerow(AEDS_CSV_HEADER)
        for aeds in graph.aeds.values():
            for aed in aeds:
                aeds_writer.writerow([
                    aed.id,
                    aed.intersection_id,
                    aed.in_use,
                    aed.open_hour,
                    aed.close_hour
                ])

    return graph