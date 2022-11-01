import pytest
from heartrunner.core.types import Intersection, Runner


def test_ids():
    for i in range(1000):
        assert Runner().id == i

    Runner.reset_id()
    assert Runner().id == 0

    assert Runner(id=10).id == 10


def test_speeds():
    for i in range(1000):
        speed = Runner().speed
        assert speed < 6 and speed > 3


def test_to_neo4j():
    with pytest.raises(AttributeError):
        Runner().to_neo4j()
    id = 1
    speed = 5
    inter = Intersection(id=id, coords=(0, 0))
    expected = {
        "id": id,
        "speed": speed,
        "intersection_id": inter.id
    }
    assert Runner(id=id, speed=speed,
                  intersection=inter).to_neo4j() == expected


# TODO: test_from_neo4j - lookinto fixtures for db mocking
