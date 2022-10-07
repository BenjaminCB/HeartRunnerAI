import logging
from random import sample
from typing import List
from neo4j import GraphDatabase, Transaction, ResultSummary
from geopy import distance
from .types import *
from .pathfinder import Graph

class HeartRunnerDB(object):

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def __enter__(self): 
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.close()

    def __batch_query(self, query: str, batch: List[dict]):
        with self.driver.session(database="neo4j") as session:
            try:
                session.run(query, batch=batch)
            except:
                logging.exception(" Error while executing __batch_query")
                return None

    def generate_runners(self, n=1) -> ResultSummary | None:
        count = self.count_nodes(NodeType.Intersection)
        n = count if n > count else n
        ids = sample(range(count), n)
        batch = [vars(Runner(intersection_id=id)) for id in ids]
        self.__batch_query(Runner.batch_merge_query(), batch)

    def generate_patients(self, n=1) -> ResultSummary | None:
        count = self.count_nodes(NodeType.Intersection)
        n = count if n > count else n
        ids = sample(range(count), n)
        batch = [vars(Patient(intersection_id=id)) for id in ids]
        self.__batch_query(Patient.batch_merge_query(), batch)

    def count_nodes(self, node_type: NodeType) -> int | None:
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(f"MATCH (n:{node_type.name}) RETURN count(n)").single()
                return result['count(n)']
            except:
                logging.exception(" Error while executing count_nodes")
                return None

    def delete_nodes(self, node_type: NodeType) -> ResultSummary | None:
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(f"MATCH (n:{node_type.name}) DETACH DELETE n").consume()
                return result
            except:
                logging.exception(" Error while executing delete_nodes")
                return None

    def get_location(self, person_type: NodeType, person_id: int) -> Intersection | None:
        with self.driver.session(database="neo4j") as session:
            try:
                result = session.run(f"MATCH (p:{person_type.name})--(i) where p.id = {person_id} RETURN i").single()
                lat = result['i']['latitude']
                lon = result['i']['longitude']
                id = result['i']['id']
                return Intersection((lat, lon), id)
            except:
                logging.exception(" Error while executing get_location")
                return None

    def get_subgraph(self, origin: tuple, kilometers=1) -> Graph | None:
        dist_limit = distance.GreatCircleDistance(kilometers=kilometers)
        north_limit = tuple(dist_limit.destination(origin, 0))
        south_limit = tuple(dist_limit.destination(origin, 180))
        east_limit = tuple(dist_limit.destination(origin, 90))
        west_limit = tuple(dist_limit.destination(origin, 270))
        limits = (north_limit[0], south_limit[0], east_limit[1], west_limit[1])
        with self.driver.session(database="neo4j") as session:
            try:
                graph = session.execute_read(self.__get_subgraph, limits)
                return graph
            except:
                logging.exception(" Error while executing get_subgraph")
                return None

    @staticmethod
    def __get_subgraph(tx: Transaction, limits: tuple) -> Graph:
        query = (
            "MATCH (i1:Intersection)-[s:Streetsegment]-(i2:Intersection) "
            f"WHERE i1.latitude <= {limits[0]} AND i1.latitude >= {limits[1]} AND i1.longitude <= {limits[2]} AND i1.longitude >= {limits[3]} "
            "OPTIONAL MATCH (i1)-[:LocatedAt]-(a:AED) "
            "OPTIONAL MATCH (i1)-[:LocatedAt]-(r:Runner) "
            "RETURN i1, i2, s, a, r "
        )
        result = tx.run(query)
        graph = Graph()
        # Parse query response into a graph 
        for record in result:
            # MATCH (i1)-[s:Streetsegment]-(i2:Intersection)
            i1_id = record['i1']['id']
            i1_coord = (record['i1']['latitude'], record['i1']['longitude'])
            i1_inter = Intersection(i1_coord, i1_id)
            graph.add_node(i1_inter)

            i2_id = record['i2']['id']
            i2_coord = (record['i2']['latitude'], record['i2']['longitude'])
            i2_inter = Intersection(i2_coord, i2_id)
            graph.add_node(i2_inter) 

            s_id = record['s']['id']
            s_length = record['s']['length']
            s_street = Streetsegment(s_id, i1_id, i2_id, s_length)
            graph.add_edge(s_street)
            
            # OPTIONAL MATCH (i1)--(a:AED)
            if record['a'] is not None:
                a_id = record['a']['id']
                a_time_range = (record['a']['open_hour'], record['a']['close_hour'])
                a_in_use = record['a']['in_use']
                aed = AED(a_id, i1_id, a_time_range, a_in_use)
                graph.add_aed(aed, i1_id)
            
            # OPTIONAL MATCH (i1)--(r:Runner)
            if record['r'] is not None:
                s_id = record['r']['id']
                speed = record['r']['speed']
                runner = Runner(s_id, speed)
                graph.add_runner(runner, i1_id)
        return graph
