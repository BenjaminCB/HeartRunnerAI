import random
import geojson
import numpy as np
from math import ceil
from neo4j import Record
from itertools import count
from dataclasses import dataclass
from abc import ABC, abstractmethod


class Entity(ABC):
    label: str
    id_iter: count

    batch_merge_query: str

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, type(self)) and __o.id == self.id

    @classmethod
    def new_id(cls) -> int:
        return next(cls.id_iter)
    
    @classmethod
    def reset_id(cls):
        cls.id_iter = count(0)

    @staticmethod
    @abstractmethod
    def from_neo4j(record: Record, **keys):
        raise NotImplementedError

    @abstractmethod
    def to_neo4j(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def to_geojson(self):
        raise NotImplementedError


class Intersection(Entity):
    label = "Intersection"
    id_iter = count(0)

    def __init__(self, coords: tuple, id=None):
        self.id = id if id else self.new_id()
        self.latitude, self.longitude = coords

    def __repr__(self) -> str:
        return f"Intersection({self.id})"

    def coords(self):
        return (self.latitude, self.longitude)

    @staticmethod
    def from_neo4j(record: Record, **keys):
        key = 'n' if 'key' not in keys else keys['key']
        id = record[key]['id']
        lat = record[key]['latitude']
        lon = record[key]['longitude']
        return Intersection(id=id, coords=(lat, lon))

    def to_neo4j(self) -> dict:
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

    def to_geojson(self):
        return geojson.Feature(
            geometry=geojson.Point((self.longitude, self.latitude)),
            properties={
                "type": self.label,
                "id": self.id
            }
        )


class AED(Entity):
    label = "AED"
    id_iter = count(0)

    _TIMERANGES = [(0, 2359), (900, 1700), (600, 2300), (300, 1200), (2000, 400)]
    _TIMERANGES_PROB = [0.4, 0.3, 0.2, 0.05, 0.05]

    def __init__(
        self, id=None, 
        intersection: Intersection=None, 
        time_range=None, 
        in_use='false'
    ):
        self.id = id if id else self.new_id()
        self.id = next(self.id_iter) if id == None else id
        if not time_range:
            time_range = random.choices(AED._TIMERANGES, AED._TIMERANGES_PROB)[0]
        self.open_hour, self.close_hour = time_range
        self.intersection = intersection
        self.in_use = in_use

    def __repr__(self) -> str:
        return f"AED({self.id})"

    @staticmethod
    def from_neo4j(record: Record, **keys):
        key = 'a' if 'key' not in keys else keys['key']
        location_key = 'n' if 'location_key' not in keys else keys['location_key']
        
        id = record[key]['id']
        open_hour = record[key]['open_hour']
        close_hour = record[key]['close_hour']
        in_use = record[key]['in_use']
        intersection = Intersection.from_neo4j(record, key=location_key)
        return AED(
            id=id,
            intersection=intersection,
            time_range=(open_hour, close_hour),
            in_use=in_use
        )

    def to_neo4j(self) -> dict:
        return {
            "id": self.id,
            "open_hour": self.open_hour,
            "close_hour": self.close_hour,
            "in_use": self.in_use,
            "intersection_id": self.intersection.id
        }

    def to_geojson(self):
        return geojson.Feature(
            geometry=geojson.Point((self.intersection.longitude, self.intersection.latitude)),
            properties={
                "type": self.label,
                "id": self.id,
                "in_use": self.in_use,
                "open_hour": self.open_hour,
                "close_hour": self.close_hour
            }
        )


class Runner(Entity):
    label = "Runner"
    id_iter = count(0)
    
    batch_merge_query = (
        "UNWIND $batch AS row "
        "MATCH (i:Intersection) WHERE i.id = row.intersection_id "
        "MERGE (r:Runner {id: row.id, speed: row.speed})-[:LocatedAt]->(i) "
    )

    def __init__(
        self, 
        id=None, 
        speed=None, 
        intersection: Intersection=None
    ):
        self.id = id if id else self.new_id()
        # self.speed = random.random()*3+3 if speed == None else speed
        self.speed = 4
        self.intersection = intersection

    def __repr__(self) -> str:
        return f"Runner({self.id})"

    @staticmethod
    def from_neo4j(record: Record, **keys):
        key = 'a' if 'key' not in keys else keys['key']
        location_key = 'n' if 'location_key' not in keys else keys['location_key']

        id = record[key]['id']
        speed = record[key]['speed']
        intersection = Intersection.from_neo4j(record, key=location_key)
        return Runner(id=id, speed=speed, intersection=intersection)

    def to_neo4j(self) -> dict:
        return {
            "id": self.id,
            "speed": self.speed,
            "intersection_id": self.intersection.id
        }

    def to_geojson(self):
        return geojson.Feature(
            geometry=geojson.Point((self.intersection.longitude, self.intersection.latitude)),
            properties={
                "type": self.label,
                "id": self.id,
                "speed": self.speed
            }
        )


class Patient(Entity):
    label = "Patient"
    id_iter = count(0)

    batch_merge_query = (
        "UNWIND $batch AS row "
        "MATCH (i:Intersection) WHERE i.id = row.intersection_id "
        "MERGE (p:Patient {id: row.id})-[:LocatedAt]->(i) "
    )

    def __init__(
        self, 
        id=None, 
        intersection: Intersection=None
    ):
        self.id = id if id else self.new_id()
        self.intersection = intersection

    def __repr__(self) -> str:
        return f"Patient({self.id})"

    @staticmethod
    def from_neo4j(record: Record, **keys):
        key = 'a' if 'key' not in keys else keys['key']
        location_key = 'n' if 'location_key' not in keys else keys['location_key']
        id = record[key]['id']
        intersection = Intersection.from_neo4j(record, key=location_key)
        return Patient(id=id, intersection=intersection)

    def to_neo4j(self) -> dict:
        return {
            "id": self.id,
            "intersection_id": self.intersection.id
        }

    def to_geojson(self):
        return geojson.Feature(
            geometry=geojson.Point((self.intersection.longitude, self.intersection.latitude)),
            properties={
                "type": self.label,
                "id": self.id
            }
        )


class Streetsegment(Entity):
    label = "Streetsegment"
    id_iter = count(0)

    def __init__(
        self,
        id: int = None,
        source: Intersection = None,
        target: Intersection = None,
        length: float = None,
        geometry: str = None
    ):
        self.id = id if id else self.new_id()
        self.source = source
        self.target = target
        self.length = length
        self.geometry = geojson.loads(geometry) if isinstance(geometry, str) else geometry

    def __hash__(self) -> int:
        return hash((self.id, self.source, self.target, self.length))

    def __eq__(self, __o: object) -> bool:
        return (
            isinstance(__o, Streetsegment) and
            self.id == __o.id and
            self.source == __o.source and
            self.target == __o.target and
            self.length == __o.length
        )

    def __repr__(self) -> str:
        return f"Street({self.id}, {self.source} <--> {self.target}, {self.length}m)"

    @staticmethod
    def from_neo4j(record: Record, **keys):
        key = 's' if 'key' not in keys else keys['key']
        head_key = 'i1' if 'head_key' not in keys else keys['head_key']
        tail_key = 'i2' if 'tail_key' not in keys else keys['tail_key']
        id = record[key]['id']
        length = record[key]['length']
        geometry = record[key]['geometry']
        source = Intersection.from_neo4j(record, key=head_key)
        target = Intersection.from_neo4j(record, key=tail_key)
        return Streetsegment(id=id, source=source, target=target, length=length, geometry=geometry)

    def to_neo4j(self) -> dict:
        return {
            "id": self.id,
            "head_id": self.source.id,
            "tail_id": self.target.id,
            "length": self.length,
            "geometry": self.geometry
        }

    def to_geojson(self):
        return geojson.Feature(
            id=self.id,
            geometry=self.geometry,
            properties={
                "type": self.label,
                "id": self.id,
                "length": self.length,
            }
        )


class Path:
    def __init__(self, source: Intersection, target: Intersection, streets: list[Streetsegment]):
        self.source = source
        self.target = target
        self.streets = streets
        self.length = sum([s.length for s in streets])
        self.aeds: set[AED] = {}

    def __repr__(self) -> str:
        rep = f"Path({self.source} -> {self.target}, {self.length}m):\n"
        for street in self.streets:
            rep += f"{street}\n"
        return rep

    def cost(self, runner: Runner):
        return ceil(self.length/runner.speed)


@dataclass
class Candidate:
    runner: Runner
    patient_path: Path
    aed_paths: list[Path]

    def patient_cost(self):
        return ceil(self.patient_path.length/self.runner.speed)

    def aed_costs(self):
        return [ceil(path.length/self.runner.speed) for path in self.aed_paths]
