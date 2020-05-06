#!/usr/bin/env python3

"""
Test settings for all test, settings are read from checkhardware.conf
"""
import logging
from .lofar import extract_select_str

logger = logging.getLogger('main.settings')
logger.debug("starting settings logger")


class TestSettings(object):
    def __init__(self, filename):
        self.parset = ParameterSet()
        self.parset.import_file(filename)

    def __call__(self):
        return self.parset

    def group(self, dev):
        pre_key = dev
        ps = ParameterSet(self.parset.make_subset(pre_key))
        return ps

    def rcumode(self, mode):
        pre_key = 'rcumode'
        if mode in (1, 3):
            pre_key += '.1-3'
        elif mode in (2, 4):
            pre_key += '.2-4'
        elif mode in (5, 6, 7):
            pre_key += '.%d' % mode
        ps = ParameterSet(self.parset.make_subset(pre_key))
        return ps


class ParameterSet(object):
    def __init__(self, data=None):
        self.parset = {}
        if data:
            if type(data) == dict:
                self.parset = data
            elif type(data) == str:
                self.import_string(data)

    def clear(self):
        self.parset = {}

    def get_set(self):
        return self.parset

    def import_file(self, filename):
        fd = open(filename, 'r')
        data = fd.readlines()
        fd.close()
        self.import_string(data)
        #for k, v in self.parset.items():
        #    logger.debug("parset: %s=%s" % (str(k), str(v)))

    def import_string(self, data):
        pre_key = ''
        for line in data:
            if line.strip() == '' or line.startswith('#'):
                continue
            if line.startswith('['):
                pre_key = line[line.find('[') + 1: line.find(']')]
                continue

            ps = self.parset
            kv_pair = line.strip().split('=')
            key = kv_pair[0]
            try:
                value = kv_pair[1]
            except IndexError:
                logger.debug("%s has no value" % key)
                value = ''
            except:
                raise
            full_key = pre_key + '.' + key
            key_list = full_key.strip().split('.')
            # print key_list, key_list[-1]

            last_key = key_list[-1]  # .replace('_', '.')
            for k in key_list[:-1]:
                # k = k.replace('_', '.')
                if k in ps:
                    ps = ps[k]
                else:
                    ps[k] = {}
                    ps = ps[k]
            ps[last_key] = value.strip()

    def make_subset(self, subset):
        keys = subset.strip().split('.')
        ps = self.parset
        for key in keys:
            ps = ps[key]
        return ps

    def replace(self, key, value):
        self.parset[key] = value

    def as_int(self, key, default=None):
        value = self.get(key, default)
        if value is None:
            return 0
        try:
            return int(value)
        except ValueError:
            logger.error("wrong conversion to integer")
            return 0
        except:
            raise

    def as_int_list(self, key, default=None):
       value_str = self.get(key, default)
       if value_str is None:
           return []
       return extract_select_str(value_str)

    def as_float(self, key, default=None):
        value = self.get(key, default)
        if value is None:
            return 0.0
        try:
            return float(value)
        except ValueError:
            logger.error("wrong conversion to float")
            return 0.0
        except:
            raise

    def as_string(self, key, default=None):
        value = self.get(key, default)
        if value is None:
            return ''
        try:
            return str(value).strip()
        except ValueError:
            logger.error("wrong conversion to string")
            return ''
        except:
            raise

    def get(self, key, default_val=None):
        ps = self.parset
        keys = key.split('.')
        try:
            for k in keys:
                ps = ps[k]
        except KeyError:
            ps = default_val
            logger.debug("key %s not found return default value" % key)
        except:
            raise
        value = ps
        return value
