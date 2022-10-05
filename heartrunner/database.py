import logging
from random import sample
import types
from neo4j import GraphDatabase, Transaction
from neo4j.exceptions import ServiceUnavailable
from geopy import distance
from .types import *
from .pathfinder import Graph

class HeartRunnerDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def rm_runners(self):
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._rm_nodes, "Runner")

    def rm_patients(self):
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._rm_nodes, "Patient")

    def _rm_nodes(tx: Transaction, node_type):
        query = (
            f'MATCH (n:{node_type}) '
            "DETACH DELETE n"
        )
        tx.run(query)

    def gen_runners(self, n=1):
        res = self._gen_persons(Runner, n)
        return list(map(Runner.row2runner, res))

    def gen_patients(self, n=1):
        res = self._gen_persons(Patient, n)
        return list(map(Patient.row2patient, res))

    def _gen_persons(self, constructor, n=1):
        res = []
        with self.driver.session(database="neo4j") as session:
            count = session.execute_read(self._intersection_count)[0]
            print(f'Intersection count: {count}')
            ids = sample(range(count), n)
            for id in ids:
                print(f'ID: {id}')
                result = session.execute_write(self._gen_person, id, constructor())
                for row in result:
                    res.append(row)
        return res

    def _gen_person(tx: Transaction, id, person):
        query = (
            "MATCH (i:Intersection) "
            "WHERE id(i) = $id "
            f'{person.create_node()} '
            "CREATE (p)-[:LocatedAt]->(i) "
            "RETURN p"
        )
        result = tx.run(query, id=id)
        try:
            return [row for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def _intersection_count(tx: Transaction):
        query = "MATCH (i:Intersection) RETURN count(*)"
        result = tx.run(query)
        try:
            return [row["count(*)"] for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def connecting_intersections(self, id):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._connecting_intersections, id)
            return result

    def _connecting_intersections(tx: Transaction, id):
        query = (
            "MATCH (:Intersection {id: $id})-[r:StreetSegment]-(i:Intersection) "
            "RETURN r,i"
        )
        result = tx.run(query, id=id)
        try:
            row2street_segment = lambda row: {"id": row["r"]["id"], "length": row["r"]["length"]}
            row2intersection = lambda row: {"id": row["i"]["id"], "x_coord": row["i"]["x_coord"], "y_coord": row["i"]["y_coord"]}
            return [(row2street_segment(row), row2intersection(row)) for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def get_subgraph(self, patient: Patient, kilometers=1):
        latitude_range = None
        longitude_range = None
        with self.driver.session(database="neo4j") as session:
            graph = session.execute_read(self._get_subgraph, latitude_range, longitude_range)
            return graph

    def _get_subgraph(tx: Transaction, lat_range, lon_range):
        query = (
            "MATCH (i1:Intersection)-[s:Streetsegment]-(i2:Intersection) "
            f"WHERE i1.latitude <= {lat_range[0]} AND i1.latitude >= {lat_range[1]} AND i1.longitude <= {lon_range[1]} AND i1.longitude >= {lon_range[0]} "
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
            s_street = StreetSegment(s_id, i1_id, i2_id, s_length)
            graph.add_edge(s_street)
            
            # OPTIONAL MATCH (i1)--(a:AED)
            if record['a'] is not None:
                a_id = record['a']['id']
                a_time_range = (record['a']['open_hour'], record['a']['close_hour'])
                a_in_use = record['a']['in_use']
                aed = Aed(a_id, i1_id, a_time_range, a_in_use)
                graph.add_aed(aed, i1_id)
            
            # OPTIONAL MATCH (i1)--(r:Runner)
            if record['r'] is not None:
                s_id = record['r']['id']
                speed = record['r']['speed']
                runner = Runner(s_id, speed)
                graph.add_runner(runner)
        
        return graph
