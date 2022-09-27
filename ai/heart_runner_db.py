from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
from runner import Runner
from patient import Patient
from random import sample


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
        self._gen_persons(Runner, n)

    def gen_pationts(self, n=1):
        self._gen_persons(Patient, n)

    def _gen_persons(self, constructor, n=1):
        with self.driver.session(database="neo4j") as session:
            count = session.execute_read(self._intersection_count)[0]
            print(count)
            ids = sample(range(count), n)
            for id in ids:
                result = session.execute_write(self._gen_person, id, constructor())
                for row in result:
                    print(row)

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
