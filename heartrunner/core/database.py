import os
import logging
from typing import Type
from dotenv import load_dotenv
from random import sample
from neo4j import GraphDatabase, Driver
from heartrunner.core.types import *
from heartrunner.core.pathfinder import Pathfinder
from heartrunner.core.util import coord_limits


class HeartrunnerDB:

    def __init__(self, uri, user, password):
        self.uri = uri
        self.auth = (user, password)
        self.driver: Driver

    def __enter__(self):
        self.driver = GraphDatabase.driver(self.uri, auth=self.auth)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.close()

    _default = None
    @staticmethod
    def default():
        if not HeartrunnerDB._default:
            load_dotenv('.env')
            uri = os.getenv("NEO4J_URI")
            user = os.getenv("NEO4J_USERNAME")
            password = os.getenv("NEO4J_PASSWORD")
            HeartrunnerDB._default = HeartrunnerDB(uri, user, password)
        return HeartrunnerDB._default

    def _batch_query(self, query: str, batch: list[dict]):
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(query, batch=batch).consume()
                return result
            except:
                logging.exception(" Error while executing __batch_query")
                return None

    def generate_entity(self, entity_cls: Type[Entity], n: int = 1):
        if entity_cls not in [Runner, Patient]:
            raise ValueError(f"{entity_cls.__name__} entities cannot be generated.")

        count = self.count_nodes(Intersection)
        n = count if n > count else n

        entities = []
        batch = []
        id_sample = sample(range(count), n)
        for location in self.get_nodes_by_id(Intersection, id_sample):
            entity = entity_cls(intersection=location)
            entities.append(entity)
            batch.append(entity.to_neo4j())
        self._batch_query(query=entity_cls.batch_merge_query, batch=batch)
        return entities

    def get_node(self, node_cls: Type[Entity], node_id: int) -> Intersection | AED | Runner | Patient:
        with self.driver.session(database="neo4j") as session:
            try:
                query = (
                    f"MATCH (n:{node_cls.label}) WHERE n.id = {node_id} "
                    f"OPTIONAL MATCH (n)-[:LocatedAt]-(m:Intersection) "
                    "RETURN n, m "
                )
                record = session.run(query).peek()
                return node_cls.from_neo4j(record, key='n', location_key='m')
            except:
                logging.exception(f" Error while executing get_node: node_type={node_cls.label}, node_id={node_id}")
                return None

    def get_nodes(self, node_cls: Type[Entity], limit=None) -> list[Intersection | AED | Runner | Patient]:
        with self.driver.session(database="neo4j") as session:
            try:
                query = (
                    f"MATCH (n:{node_cls.label}) "
                    f"OPTIONAL MATCH (n)-[:LocatedAt]-(m:Intersection) "
                    "RETURN n, m "
                )
                if limit:
                    query += f"LIMIT {limit} "
                
                result = session.run(query)
                return [node_cls.from_neo4j(record, key='n', location_key='m') for record in result]
            except:
                logging.exception(" Error while executing get_nodes")
                return None

    def get_nodes_by_id(self, node_cls: Type[Entity], ids: list[int]):
        with self.driver.session(database="neo4j") as session:
            try:
                query = (
                    f"MATCH (n:{node_cls.label}) WHERE n.id IN {ids} "
                    f"OPTIONAL MATCH (n)-[:LocatedAt]-(m:Intersection) "
                    "RETURN n, m "
                )
                result = session.run(query)
                return [node_cls.from_neo4j(record, key='n', location_key='m') for record in result]
            except:
                logging.exception(" Error while executing get_nodes_by_id")
                return None

    def delete_nodes(self, node_cls: Type[Entity]):
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(f"MATCH (n:{node_cls.label}) DETACH DELETE n").consume()
                return result
            except:
                logging.exception(" Error while executing delete_nodes")
                return None

    def delete_nodes_by_id(self, node_cls: Type[Entity], ids: list[int]):
        with self.driver.session(database="neo4j") as session:
            try:
                query = (
                    f"MATCH (n:{node_cls.label}) WHERE n.id IN {ids} "
                    "DETACH DELETE n"
                )
                result = session.run(query).consume()
                return result
            except:
                logging.exception(" Error while executing get_nodes_by_id")
                return None

    def count_nodes(self, node_cls: Type[Entity]):
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(f"MATCH (n:{node_cls.label}) RETURN count(n)").single()
                return result['count(n)']
            except:
                logging.exception(" Error while executing count_nodes")
                return None

    def get_pathfinder(self, patient: Patient, kilometers=1):
        with self.driver.session(database="neo4j") as session:
            patient_coords = self.get_node(Intersection, patient.intersection.id).coords()
            limits = coord_limits(origin=patient_coords, range=kilometers)
            try:
                query = (
                    "MATCH (i1:Intersection)-[s:Streetsegment]-(i2:Intersection) "
                    f"WHERE i1.latitude <= {limits[0]} AND i1.latitude >= {limits[1]} AND i1.longitude <= {limits[2]} AND i1.longitude >= {limits[3]} "
                    "OPTIONAL MATCH (i1)-[:LocatedAt]-(a:AED) "
                    "OPTIONAL MATCH (i1)-[:LocatedAt]-(r:Runner) "
                    "RETURN i1, i2, s, a, r "
                )
                result = session.run(query)
                pf = Pathfinder(patient)
                for record in result:
                    # MATCH (i1)-[s:Streetsegment]-(i2:Intersection)
                    pf.add_edge(edge=Streetsegment.from_neo4j(record, key='s', head_key='i1', tail_key='i2'))
                    
                    # OPTIONAL MATCH (i1)--(a:AED)
                    if record['a']:
                        pf.add_aed(aed=AED.from_neo4j(record, key='a', location_key='i1'))

                    # OPTIONAL MATCH (i1)--(r:Runner)      
                    if record['r']:
                        pf.add_runner(runner=Runner.from_neo4j(record, key='r', location_key='i1'))
                return pf
            except:
                logging.exception(" Error while executing get_pathfinder")
                return None
