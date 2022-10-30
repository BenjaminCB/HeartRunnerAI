import math
import csv
import geojson
import geojson_length
from geopy.distance import great_circle
from heartrunner.types import Intersection, Streetsegment, AED
from heartrunner.settings import *


def parse_geojson(streets_path=STREETS_GEOJSON_PATH, aeds_path=AEDS_GEOJSON_PATH):
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
        open(streets_path, "r") as streets_file,
        open(aeds_path, "r") as aeds_file
    ):
        intersections: dict[tuple, Intersection] = {}
        streetsegments: list[Streetsegment] = []
        aeds: list[AED] = []
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

            streetsegments.append(Streetsegment(
                source=intersections[head_coords],
                target=intersections[tail_coords],
                length=length,
                geometry=feature["geometry"]
            ))

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

            aeds.append(AED(intersection=closest_inter))

    with (
        open(INTERSECTIONS_CSV_PATH, "w+") as intersections_file,
        open(STREETS_CSV_PATH, "w+") as streets_file,
        open(AEDS_CSV_PATH, "w+") as aeds_file
    ):
        intersections_writer = csv.writer(intersections_file)
        streets_writer = csv.writer(streets_file)
        aeds_writer = csv.writer(aeds_file)

        intersections_writer.writerow(INTERSECTIONS_CSV_HEADER)
        for intersection in intersections.values():
            intersections_writer.writerow([
                intersection.id,
                intersection.latitude,
                intersection.longitude
            ])

        streets_writer.writerow(STREETS_CSV_HEADER)
        for street in streetsegments:
            streets_writer.writerow([
                street.id,
                street.source.id,
                street.target.id,
                street.length,
                street.geometry
            ])

        aeds_writer.writerow(AEDS_CSV_HEADER)
        for aed in aeds:
            aeds_writer.writerow([
                aed.id,
                aed.intersection.id,
                aed.in_use,
                aed.open_hour,
                aed.close_hour
            ])


def coord_limits(origin: tuple, range: float):
    dist_limit = great_circle(kilometers=range)

    north_limit = dist_limit.destination(origin, 0).latitude
    south_limit = dist_limit.destination(origin, 180).latitude
    east_limit = dist_limit.destination(origin, 90).longitude
    west_limit = dist_limit.destination(origin, 270).longitude

    return (north_limit, south_limit, east_limit, west_limit)
