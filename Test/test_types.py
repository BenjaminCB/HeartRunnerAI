from heartrunner.HRtypes import *


# Test class for grouping of test
class TestTypes:
    runner = Runner
    #patient = Patient
    #intersection = Intersection
    #aed = AED

    # Test functions
    def test_Runner(self):
        runnerId = self.runner.id_iter
        assert runnerId != 0