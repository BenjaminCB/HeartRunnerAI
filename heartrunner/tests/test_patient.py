import pytest
from heartrunner.core.types import Patient, Intersection

def test_ids():
    for i in range(1000):
        assert Patient().id == i
    
    Patient.reset_id()
    assert Patient().id == 0

    assert Patient(id=10).id == 10


def test_to_neo4j():
    with pytest.raises(AttributeError):
        Patient().to_neo4j()
    id = 1
    inter = Intersection(id=id, coords=(0,0))
    expected = {
        "id": id,
        "intersection_id": inter.id
    }
    assert Patient(id=id, intersection=inter).to_neo4j() == expected


# TODO: test_from_neo4j - lookinto fixtures for db mocking
