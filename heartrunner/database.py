import os
import logging
from dotenv import load_dotenv
from random import sample
from neo4j import GraphDatabase, Driver
from heartrunner.types import *
from heartrunner.pathfinder import Pathfinder
from heartrunner.util import coord_limits


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

    def generate_runners(self, n=1):
        count = self.count_nodes(NodeType.Intersection)
        n = count if n > count else n
        
        runners: list[Runner] = []
        batch = []
        ids = sample(range(count), n)
        for id in ids:
            runner = Runner(intersection_id=id)
            runners.append(runner)
            batch.append(vars(runner))

        query = (
            "UNWIND $batch AS row "
            "MATCH (i:Intersection) WHERE i.id = row.intersection_id "
            "MERGE (r:Runner {id: row.id, speed: row.speed})-[:LocatedAt]->(i) "
        )
        self._batch_query(query, batch)
        return runners

    def generate_patients(self, n=1):
        count = self.count_nodes(NodeType.Intersection)
        n = count if n > count else n

        patients: list[Patient] = []
        batch = []
        ids = sample(range(count), n)
        for id in ids:
            patient = Patient(intersection_id=id)
            patients.append(patient)
            batch.append(vars(patient))

        query = (
            "UNWIND $batch AS row "
            "MATCH (i:Intersection) WHERE i.id = row.intersection_id "
            "MERGE (p:Patient {id: row.id})-[:LocatedAt]->(i) "
        )
        self._batch_query(query, batch)
        return patients

    def get_node(self, node_type: NodeType, node_id: int):
        with self.driver.session(database="neo4j") as session:
            try:
                query = (
                    f"MATCH (n:{node_type.name}) WHERE n.id = {node_id} "
                    f"OPTIONAL MATCH (n)-[:LocatedAt]-(m:Intersection) "
                    "RETURN n, m "
                )
                result = session.run(query).peek()
                match node_type:
                    case NodeType.Patient:
                        return Patient.from_neo4j(result)
                    case NodeType.Runner:
                        return Runner.from_neo4j(result)
                    case NodeType.AED:
                        return AED.from_neo4j(result)
                    case NodeType.Intersection:
                        return Intersection.from_neo4j(result)
            except:
                logging.exception(f" Error while executing get_node: node_type={node_type.name}, node_id={node_id}")
                return None

    def get_nodes(self, node_type: NodeType, limit=None):
        with self.driver.session(database="neo4j") as session:
            try:
                query = (
                    f"MATCH (n:{node_type.name}) "
                    f"OPTIONAL MATCH (n)-[:LocatedAt]-(m:Intersection) "
                    "RETURN n, m "
                )
                if limit:
                    query += f"LIMIT {limit} "
                
                result = session.run(query)
                nodes = []
                for record in result:
                    match node_type:
                        case NodeType.Patient:
                            nodes.append(Patient.from_neo4j(record))
                        case NodeType.Runner:
                            nodes.append(Runner.from_neo4j(record))
                        case NodeType.AED:
                            nodes.append(AED.from_neo4j(record))
                        case NodeType.Intersection:
                            nodes.append(Intersection.from_neo4j(record))
                return nodes
            except:
                logging.exception(" Error while executing get_nodes")
                return None

    def delete_nodes(self, node_type: NodeType):
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(
                    f"MATCH (n:{node_type.name}) DETACH DELETE n").consume()
                return result
            except:
                logging.exception(" Error while executing delete_nodes")
                return None

    def count_nodes(self, node_type: NodeType):
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(
                    f"MATCH (n:{node_type.name}) RETURN count(n)").single()
                return result['count(n)']
            except:
                logging.exception(" Error while executing count_nodes")
                return None

    def get_pathfinder(self, patient: Patient, kilometers=1):
        with self.driver.session(database="neo4j") as session:
            patient_coords = self.get_node(NodeType.Intersection, patient.intersection_id).coords()
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
                return Pathfinder.from_neo4j(result, patient)
            except:
                logging.exception(" Error while executing get_pathfinder")
                return None
