from heartrunner.types import Patient, Runner


def test_runner_ids():
    for i in range(1000):
        r = Runner()
        assert r.id == i
    


def test_runner_speeds():
    for i in range(1000):
        r = Runner()
        assert r.speed > 3 and r.speed < 6


# TODO: test_runner_from_neo4j


def test_patient_ids():
    for i in range(1000):
        p = Patient()
        assert p.id == i

    assert Patient(id=1).id == 1


# TODO: test_patient_from_neo4j