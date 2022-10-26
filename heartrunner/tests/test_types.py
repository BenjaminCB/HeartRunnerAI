from heartrunner.types import Runner

def test_runner_ids():
    for i in range(100):
        r = Runner()
    r = Runner()
    assert r.id == 100 

