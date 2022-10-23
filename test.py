import unittest

# Import functions from files here:
import heartrunner.HRtypes


# Basic Test class 
class TestTypes(unittest.TestCase):

    runner = heartrunner.HRtypes.Runner
    patient = heartrunner.HRtypes.Patient

    # Test case function
    def test_Runner(self):
        runnerId = self.runner.id_iter
        self.assertIsNotNone(runnerId)

    def test_patient(self):
        patientId = self.patient.id_iter
        self.assertIsNotNone(patientId)

if __name__ == '__main__':  
    # begin the unittest.main()  
    unittest.main()  