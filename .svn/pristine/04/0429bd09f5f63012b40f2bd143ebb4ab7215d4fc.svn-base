#!/usr/bin/env python

# Copyright (C) 2017
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

import unittest
from lofarpipe.recipes.helpers.metadata import *
from numpy import *
import mock

import logging
logger = logging.getLogger(__name__)

class AbstractMockTable:
    '''a mocked version of the pyrap.tables.table class,
    can be used with dependency injection in the tests'''
    def __init__(self, *args, **kwargs):
        pass

    def getkeyword(self, *args, **kwargs):
        return ''

    def getcell(self, name, default=None):
        return default

    def nrows(self):
        return 0

    def getdminfo(self, columnname):
        return {}

class LofarMockTable(AbstractMockTable):
    def getdminfo(self, columnname):
        assert columnname == 'DATA'
        # return a real world example of datamanager info from a MS with a LofarStMan
        return {'NAME': 'LofarStMan',
                'SEQNR': 0,
                'SPEC': {'alignment': 512,
                         'bigEndian': False,
                         'maxNrSample': 3056.0,
                         'nbaseline': 741,
                         'nrBytesPerNrValidSamples': 2,
                         'startTime': 5022530520.500695,
                         'timeInterval': 1.00139008,
                         'useSeqnrFile': True,
                         'version': 3},
                'TYPE': 'LofarStMan'}

class DyscoMockTable(AbstractMockTable):
    def getdminfo(self, columnname):
        assert columnname == 'DATA'
        # return a real world example of datamanager info from a MS with a DyscoStMan
        return {'NAME': 'DyscoData',
                'SEQNR': 3,
                'SPEC': {'dataBitCount': 10,
                         'distribution': 'TruncatedGaussian',
                         'distributionTruncation': 2.5,
                         'normalization': 'AF',
                         'studentTNu': 0.0,
                         'weightBitCount': 12},
                'TYPE': 'DyscoStMan'}

class CasaTiledMockTable(AbstractMockTable):
    def getdminfo(self, columnname):
        assert columnname == 'DATA'
        # return a real world example of datamanager info from a MS with a TiledColumnStMan
        return {'NAME': 'TiledFlag',
                'SEQNR': 4,
                'SPEC': {'ActualMaxCacheSize': 0,
                         'DEFAULTTILESHAPE': array([4, 4, 65536], dtype=int32),
                         'HYPERCUBES': {'*1': {'BucketSize': 131072,
                                               'CellShape': array([4, 4], dtype=int32),
                                               'CubeShape': array([4, 4, 5993949], dtype=int32),
                                               'ID': {},
                                               'TileShape': array([4, 4, 65536], dtype=int32)}},
                         'MAXIMUMCACHESIZE': 0,
                         'SEQNR': 4},
                'TYPE': 'TiledColumnStMan'}

class CasaStandardMockTable(AbstractMockTable):
    def getdminfo(self, columnname):
        assert columnname == 'DATA'
        # return a real world example of datamanager info from a MS with a StandardStMan
        return {'NAME': 'SSMVar',
                'SEQNR': 0,
                'SPEC': {'ActualCacheSize': 2,
                         'BUCKETSIZE': 32768,
                         'IndexLength': 11830,
                         'PERSCACHESIZE': 2},
                'TYPE': 'StandardStMan'}


# for some reason, the casa and dysco versions are 'encoded' in the running environment
# define the here and set them for this test in the enviroment
CASA_VERSION = "2.2.0"
DYSCO_VERSION = "1.01"
os.environ['CASACORE_VERSION'] = CASA_VERSION
os.environ['DYSCO_VERSION'] = DYSCO_VERSION


class StorageWriterTypesTest(unittest.TestCase):
    '''
    Tests the StorageWriterTypes class
    '''

    def test_get_type_and_version_casa_standard(self):
        main = CasaStandardMockTable()
        sw_type, sw_version = StorageWriterTypes.get_type_and_version(main)
        self.assertEqual(StorageWriterTypes.CASA, sw_type)
        self.assertEqual(CASA_VERSION, sw_version)

    def test_get_type_and_version_casa_tiled(self):
        main = CasaTiledMockTable()
        sw_type, sw_version = StorageWriterTypes.get_type_and_version(main)
        self.assertEqual(StorageWriterTypes.CASA, sw_type)
        self.assertEqual(CASA_VERSION, sw_version)

    def test_get_type_and_version_dysco(self):
        main = DyscoMockTable()
        sw_type, sw_version = StorageWriterTypes.get_type_and_version(main)
        self.assertEqual(StorageWriterTypes.DYSCO, sw_type)
        self.assertEqual(DYSCO_VERSION, sw_version)

    def test_get_type_and_version_lofar(self):
        main = LofarMockTable()
        sw_type, sw_version = StorageWriterTypes.get_type_and_version(main)
        self.assertEqual(StorageWriterTypes.LOFAR, sw_type)
        self.assertEqual(3, sw_version)

    def test_get_type_and_version_unknown(self):
        main = AbstractMockTable()
        sw_type, sw_version = StorageWriterTypes.get_type_and_version(main)
        self.assertEqual(StorageWriterTypes.UNKNOWN, sw_type)
        self.assertEqual(StorageWriterTypes.UNKNOWN_VERSION, sw_version)


class MetaDataTest(unittest.TestCase):
    '''
    Tests the creation of correct meta data parsets
    '''

    def test_correlated_casa_standard(self):
        with mock.patch('pyrap.tables.table', new=CasaStandardMockTable):
            dataproduct_metadata = Correlated(logger=None, filename='casa-standard')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('casa_standard metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.CASA, metadata_parset.getString('storageWriter'))
            self.assertEqual(CASA_VERSION, metadata_parset.getString('storageWriterVersion'))

    def test_correlated_casa_tiled(self):
        with mock.patch('pyrap.tables.table', new=CasaTiledMockTable):
            dataproduct_metadata = Correlated(logger=None, filename='casa-tiled')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('casa_lofar metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.CASA, metadata_parset.getString('storageWriter'))
            self.assertEqual(CASA_VERSION, metadata_parset.getString('storageWriterVersion'))

    def test_correlated_lofar(self):
        with mock.patch('pyrap.tables.table', new=LofarMockTable):
            dataproduct_metadata = Correlated(logger=None, filename='lofar')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('lofar metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.LOFAR, metadata_parset.getString('storageWriter'))
            self.assertEqual('3', metadata_parset.getString('storageWriterVersion'))

    def test_correlated_dysco(self):
        with mock.patch('pyrap.tables.table', new=DyscoMockTable):
            dataproduct_metadata = Correlated(logger=None, filename='dysco')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('dysco metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.DYSCO, metadata_parset.getString('storageWriter'))
            self.assertEqual(DYSCO_VERSION, metadata_parset.getString('storageWriterVersion'))

    def test_correlated_unknown(self):
        with mock.patch('pyrap.tables.table', new=AbstractMockTable):
            dataproduct_metadata = Correlated(logger=None, filename='foo.bar')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('unknown metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.UNKNOWN, metadata_parset.getString('storageWriter'))
            self.assertEqual(StorageWriterTypes.UNKNOWN_VERSION, metadata_parset.getString('storageWriterVersion'))

    def test_instrument_model(self):
        with mock.patch('pyrap.images.image'):
            dataproduct_metadata = InstrumentModel(logger=None, filename='foo.INST')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('instrument model metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.CASA, metadata_parset.getString('storageWriter'))
            self.assertEqual(CASA_VERSION, metadata_parset.getString('storageWriterVersion'))

    def test_skyimage_h5(self):
        with mock.patch('pyrap.images.image'):
            dataproduct_metadata = SkyImage(logger=None, filename='foo.h5')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('instrument model metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.HDF5DEFAULT, metadata_parset.getString('storageWriter'))
            self.assertEqual(StorageWriterTypes.UNKNOWN_VERSION, metadata_parset.getString('storageWriterVersion'))

    def test_skyimage_casa(self):
        with mock.patch('pyrap.images.image'):
            dataproduct_metadata = SkyImage(logger=None, filename='foo.IM')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('instrument model metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.CASA, metadata_parset.getString('storageWriter'))
            self.assertEqual(CASA_VERSION, metadata_parset.getString('storageWriterVersion'))

    def test_skyimage_other(self):
        with mock.patch('pyrap.images.image'):
            dataproduct_metadata = SkyImage(logger=None, filename='foo.fits')
            metadata_parset = dataproduct_metadata.as_parameterset()
            logger.info('instrument model metadata parset:\n%s', metadata_parset)
            self.assertEqual(StorageWriterTypes.UNKNOWN, metadata_parset.getString('storageWriter'))
            self.assertEqual(StorageWriterTypes.UNKNOWN_VERSION, metadata_parset.getString('storageWriterVersion'))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    unittest.main()

