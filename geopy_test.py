import os
from neo4j import Transaction, Record
from geopy import distance
from dotenv import load_dotenv
from heartrunner.database import HeartRunnerDB


def tx_function(tx: Transaction, lat_range, lon_range):
    query = (
        "MATCH (i:Intersection)-[r]-(a) "
        f"WHERE i.latitude <= {lat_range[0]} AND i.latitude >= {lat_range[1]} AND i.longitude <= {lon_range[1]} AND i.longitude >= {lon_range[0]} "
        "RETURN a, r, i "
    )
    print(query)
    result = tx.run(query)
    for record in result:
        # print(record)
        print(record['r']['id'])
    return result.data()

if __name__ == "__main__":
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    load_dotenv('.env')
    # uri = "neo4j+s://10ef08ec.databases.neo4j.io"
    # user = "neo4j"
    # password = "lymMxxE2BKuotSVbZPzpBTzg_IMDqrWkHcNcoAU8R3M"
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    db = HeartRunnerDB(uri, user, password)

    origin = (38.908139,-76.968721)

    dist_limit = distance.GreatCircleDistance(meters=500)
    print(f'Origin: {origin}')
    north_limit = tuple(dist_limit.destination(origin, 0))
    print(f'North limit: {north_limit}')
    south_limit = tuple(dist_limit.destination(origin, 180))
    print(f'South limit: {south_limit}')
    east_limit = tuple(dist_limit.destination(origin, 90))
    print(f'East limit: {east_limit}')
    west_limit = tuple(dist_limit.destination(origin, 270))
    print(f'West limit: {west_limit}')

    latitude_range = (north_limit[0], south_limit[0])
    longitude_range = (west_limit[1], east_limit[1])

    with db.driver.session(database="neo4j") as session:
        res = session.execute_read(tx_function, latitude_range, longitude_range)
        

    db.close()