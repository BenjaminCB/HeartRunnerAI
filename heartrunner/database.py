import logging
from random import sample
from neo4j import GraphDatabase, Transaction
from geopy.distance import great_circle
from .types import *
from .pathfinder import Pathfinder


class HeartrunnerDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.close()

    def __batch_query(self, query: str, batch: list[dict]):
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
        ids = sample(range(count), n)
        batch = [vars(Runner(intersection_id=id)) for id in ids]
        query = (
            "UNWIND $batch AS row "
            "MATCH (i:Intersection) WHERE i.id = row.intersection_id "
            "MERGE (r:Runner {id: row.id, speed: row.speed})-[:LocatedAt]->(i) "
        )
        self.__batch_query(query, batch)

    def generate_patients(self, n=1):
        count = self.count_nodes(NodeType.Intersection)
        n = count if n > count else n
        ids = sample(range(count), n)
        batch = [vars(Patient(intersection_id=id)) for id in ids]
        query = (
            "UNWIND $batch AS row "
            "MATCH (i:Intersection) WHERE i.id = row.intersection_id "
            "MERGE (p:Patient {id: row.id})-[:LocatedAt]->(i) "
        )
        self.__batch_query(query, batch)

    def get_node(self, node_type: NodeType, node_id: int):
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(
                    f"MATCH (n:{node_type.name})--(m) WHERE n.id = {node_id} RETURN n, m").peek()
                match node_type:
                    case NodeType.Patient:
                        return Patient.from_record(result)
                    case NodeType.Runner:
                        return Runner.from_record(result)
                    case NodeType.AED:
                        return AED.from_record(result)
                    case NodeType.Intersection:
                        return Intersection.from_record(result)
            except:
                logging.exception(" Error while executing get_node")
                return None

    def get_nodes(self, node_type: NodeType, limit=0):
        with self.driver.session(database="neo4j") as session:
            try:
                query = f"MATCH (n:{node_type.name})--(m) RETURN n, m"
                if limit > 0:
                    query += f" LIMIT {limit}"
                result = session.run(query)
                nodes = []
                for record in result:
                    match node_type:
                        case NodeType.Patient:
                            nodes.append(Patient.from_record(record))
                        case NodeType.Runner:
                            nodes.append(Runner.from_record(record))
                        case NodeType.AED:
                            nodes.append(AED.from_record(record))
                        case NodeType.Intersection:
                            nodes.append(Intersection.from_record(record))
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
            try:
                location = self.get_node(
                    NodeType.Intersection, patient.intersection_id).coords()
                dist_limit = great_circle(kilometers=kilometers)
                north_limit = tuple(dist_limit.destination(location, 0))
                south_limit = tuple(dist_limit.destination(location, 180))
                east_limit = tuple(dist_limit.destination(location, 90))
                west_limit = tuple(dist_limit.destination(location, 270))
                limits = (north_limit[0], south_limit[0],
                          east_limit[1], west_limit[1])

                graph = session.execute_read(
                    self.__get_pathfinder, limits, patient)
                return graph
            except:
                logging.exception(" Error while executing get_subgraph")
                return None

    @staticmethod
    def __get_pathfinder(tx: Transaction, limits: tuple, patient: Patient):
        query = (
            "MATCH (i1:Intersection)-[s:Streetsegment]-(i2:Intersection) "
            f"WHERE i1.latitude <= {limits[0]} AND i1.latitude >= {limits[1]} AND i1.longitude <= {limits[2]} AND i1.longitude >= {limits[3]} "
            "OPTIONAL MATCH (i1)-[:LocatedAt]-(a:AED) "
            "OPTIONAL MATCH (i1)-[:LocatedAt]-(r:Runner) "
            "RETURN i1, i2, s, a, r "
        )
        result = tx.run(query)
        pf = Pathfinder(patient)
        # Parse query response into a pathfinder instance
        for record in result:
            # MATCH (i1)-[s:Streetsegment]-(i2:Intersection)
            i1_id = record['i1']['id']
            i1_coord = (record['i1']['latitude'], record['i1']['longitude'])
            i1 = Intersection(id=i1_id, coords=i1_coord)

            i2_id = record['i2']['id']
            i2_coord = (record['i2']['latitude'], record['i2']['longitude'])
            i2 = Intersection(id=i2_id, coords=i2_coord)

            s_id = record['s']['id']
            s_length = record['s']['length']
            s_geometry = record['s']['geometry']
            s = Streetsegment(
                id=s_id,
                source=i1,
                target=i2,
                length=s_length,
                geometry=s_geometry
            )
            pf.add_edge(edge=s)

            # OPTIONAL MATCH (i1)--(a:AED)
            if record['a']:
                a_id = record['a']['id']
                a_time_range = (record['a']['open_hour'],
                                record['a']['close_hour'])
                a_in_use = record['a']['in_use']
                a = AED(
                    id=a_id,
                    intersection_id=i1_id,
                    time_range=a_time_range,
                    in_use=a_in_use
                )
                pf.add_aed(aed=a)

            # OPTIONAL MATCH (i1)--(r:Runner)
            if record['r']:
                r_id = record['r']['id']
                speed = record['r']['speed']
                r = Runner(id=r_id, speed=speed, intersection_id=i1_id)
                pf.add_runner(runner=r)
        return pf
