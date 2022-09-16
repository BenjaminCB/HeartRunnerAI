https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/RunnerLocations.csv

# import runners
LOAD CSV WITH HEADERS FROM 'https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/Runners.csv' AS row
CREATE (r:Runner)
SET r.name = row.name, r.speed = toInteger(row.speed)

# import patients
LOAD CSV WITH HEADERS FROM 'https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/Patients.csv' AS row
CREATE (p:Patient)
SET p.name = row.name

# import Intersections
LOAD CSV WITH HEADERS FROM 'https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/Intersections.csv' AS row
CREATE (i:Intersection)
SET i.id = row.id

# import AEDs
LOAD CSV WITH HEADERS FROM 'https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/AEDs.csv' AS row
CREATE (a:AED)
SET a.id = row.id, a.available=row.available

# constraints
CREATE CONSTRAINT UniqueRunnerNameConstraint ON (r:Runner) ASSERT r.name IS UNIQUE
CREATE CONSTRAINT UniquePatientNameConstraint ON (p:Patient) ASSERT p.name IS UNIQUE
CREATE CONSTRAINT UniqueIntersectionIdConstraint ON (i:Intersection) ASSERT i.id IS UNIQUE
CREATE CONSTRAINT UniqueAEDIdConstraint ON (a:AED) ASSERT a.id IS UNIQUE

# make street segments
LOAD CSV WITH HEADERS FROM 'https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/StreetSegments.csv' AS row
MATCH
    (a:Intersection {id: row.intersection_a}),
    (b:Intersection {id: row.intersection_b})
CREATE (a)-[r:Connects {id: a.id + '->' + b.id, length: row.length, difficulty: row.difficulty}]->(b)
RETURN type(r), r.id

# make runner locations
LOAD CSV WITH HEADERS FROM 'https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/RunnerLocations.csv' AS row
MATCH
    (r:Runner {name: row.runner_name}),
    (i:Intersection {id: row.intersection_id})
CREATE (r)-[:Located]->(i)
RETURN r.name,i.id

# make patient locations
LOAD CSV WITH HEADERS FROM 'https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/PatientLocations.csv' AS row
MATCH
    (p:Patient {name: row.patient_name}),
    (i:Intersection {id: row.intersection_id})
CREATE (p)-[:Located]->(i)
RETURN p.name,i.id

# make aed locations
LOAD CSV WITH HEADERS FROM 'https://gitlab.com/Ace_BCB/heartrunnerai/-/raw/main/csvs/AEDLocations.csv' AS row
MATCH
    (a:AED {id: row.aed_id}),
    (i:Intersection {id: row.intersection_id})
CREATE (a)-[:Located]->(i)
RETURN a.id,i.id
