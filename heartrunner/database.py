import logging
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from random import sample
from .types import Patient, Runner


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

    @staticmethod
    def _rm_nodes(tx, node_type):
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
                result = session.execute_write(self._gen_person, id, constructor())
                for row in result:
                    res.append(row)
        return res

    @staticmethod
    def _gen_person(tx, id, person):
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

    @staticmethod
    def _intersection_count(tx):
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

    @staticmethod
    def _connecting_intersections(tx, id):
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
