import unittest
from unittest.mock import MagicMock
from lofar.sas.resourceassignment.ratootdbtaskspecificationpropagator.translator import RAtoOTDBTranslator, PREFIX
from lofar.sas.resourceassignment.common.specification import Specification
import datetime


class RAtoOTDBPropagatorTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_CreateParset_returns_storagemanager_from_MoM_as_DPPP_parameter(self):

        # test values:
        otdb_id = 123

        start = datetime.datetime.utcnow()
        end = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        ra_info = {"starttime" : start, "endtime": end, "status": "test_in_progress", "type": "test", "cluster": "CEP4"}

        project_name = "myproject"

        storagemanager = "d.y.s.c.o."
        mom_info = Specification(None, None, None)
        mom_info.storagemanager = storagemanager

        # trigger action:
        value = RAtoOTDBTranslator().CreateParset(otdb_id, ra_info, project_name, mom_info)

        # assert:
        self.assertEqual(value[PREFIX+"ObservationControl.PythonControl.DPPP.msout.storagemanager.name"], storagemanager)


if __name__ == "__main__":
    unittest.main()

