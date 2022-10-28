import imp
import unittest

# Import functions from files here:
import heartrunner.HRtypes
import heartrunner.pathfinder


# Basic Test class 
class TestTypes(unittest.TestCase):
    runner = heartrunner.HRtypes.Runner
    patient = heartrunner.HRtypes.Patient
    intersection = heartrunner.HRtypes.Intersection
    aed = heartrunner.HRtypes.AED

    # Test case function
    def test_Runner(self):
        runnerId = self.runner.id_iter
        self.assertIsNotNone(runnerId)

    def test_patient(self):
        patientId = self.patient.id_iter
        self.assertIsNotNone(patientId)
    
    def test_intersection(self):
        intersectionId = self.intersection.id_iter
        self.assertIsNotNone(intersectionId)

    def test_aed(self):
        aedId = self.aed.id_iter
        self.assertIsNotNone(aedId)



class TestPathfinder(unittest.TestCase):
    def get_AED(self):
        self.assertIs(heartrunner.pathfinder.Pathfinder.get_aeds, heartrunner.HRtypes.AED)


if __name__ == '__main__':  
    # begin the unittest.main()  
    unittest.main()  