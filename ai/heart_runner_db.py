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
        with self.driver.session(database="neo4j") as session:
            count = session.execute_read(self._intersection_count)[0]
            print(count)
            ids = sample(range(count), n)
            for id in ids:
                result = session.execute_write(self._gen_runner, id)
                for row in result:
                    print(row)

    @staticmethod
    def _gen_runner(tx, id):
        query = (
            "MATCH (i:Intersection) "
            "WHERE id(i) = $id "
            f'{Runner().create_node()} '
            "CREATE (r)-[:LocatedAt]->(i) "
            "RETURN r"
        )
        result = tx.run(query, id=id)
        try:
            return [{"id": row["r"]["id"], "speed": row["r"]["speed"]} for row in result]
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

    def create_friendship(self, person1_name, person2_name):
        with self.driver.session(database="neo4j") as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.execute_write(
                self._create_and_return_friendship, person1_name, person2_name)
            for row in result:
                print("Created friendship between: {p1}, {p2}".format(p1=row['p1'], p2=row['p2']))

    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1, p2"
        )
        result = tx.run(query, person1_name=person1_name, person2_name=person2_name)
        try:
            return [{"p1": row["p1"]["name"], "p2": row["p2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_person(self, person_name):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._find_and_return_person, person_name)
            for row in result:
                print("Found person: {row}".format(row=row))

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [row["name"] for row in result]
