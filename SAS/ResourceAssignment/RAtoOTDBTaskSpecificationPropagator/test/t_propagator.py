import unittest
from unittest.mock import MagicMock
from lofar.sas.resourceassignment.ratootdbtaskspecificationpropagator.propagator import RAtoOTDBPropagator
from lofar.sas.resourceassignment.common.specification import Specification


class RAtoOTDBPropagatorTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_doTaskScheduled_calls_CreateParset_with_correct_info(self):

        # test values
        raid = 1
        otdbid = 2
        momid = 3
        rainfo = {'ra': 'info'}
        mominfo = Specification(None, None, None)
        projectname = 'myproject'
        parset = 'par-set'

        # setup mocks
        prop = RAtoOTDBPropagator()
        prop.getRAinfo = MagicMock(return_value=rainfo)
        prop.getMoMinfo = MagicMock(return_value=mominfo)
        prop.momrpc.getObjectDetails = MagicMock(return_value={momid:{'project_name':projectname}})
        prop.translator.CreateParset = MagicMock(return_value=parset)
        prop.setOTDBinfo = MagicMock()

        # trigger test action
        prop.doTaskScheduled(raid, otdbid, momid)

        # assert info was gathered with correct id and createparsec is called with the returned info
        prop.getRAinfo.assert_called_once_with(raid)
        prop.getMoMinfo.assert_called_once_with(momid)
        prop.momrpc.getObjectDetails.assert_called_once_with(momid)
        prop.translator.CreateParset.assert_called_once_with(otdbid, rainfo, projectname, mominfo)
        prop.setOTDBinfo.assert_called_once_with(otdbid, parset, 'scheduled')

    def test_getMoMinfo_returns_storagemanager_from_MoM(self):

        # test values
        momid = 3
        storagemanager = "d.y.s.c.o"

        # setup mocks
        prop = RAtoOTDBPropagator()
        prop.momrpc = MagicMock()
        prop.momrpc.get_storagemanager.return_value = storagemanager

        # trigger test action
        mominfo = prop.getMoMinfo(momid)

        # assert momrpc is called with correct id
        prop.momrpc.get_storagemanager.assert_called_once_with(momid)
        # assert returned value by mom is part of spec (yes, that should strictly not be tested here)
        self.assertEqual(mominfo.storagemanager, storagemanager)


if __name__ == "__main__":
    unittest.main()

