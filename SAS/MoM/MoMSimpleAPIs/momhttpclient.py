#!/usr/bin/env python3

import requests
from time import  sleep

import logging
logger = logging.getLogger()

from lofar.common import isProductionEnvironment

import urllib3
urllib3.disable_warnings()

class BaseMoMClient:
    MOM_BASE_URL = 'https://lcs023.control.lofar:8443/' if isProductionEnvironment() else 'http://lofartest.control.lofar:8080/'

    def __init__(self, mom_base_url, user = None, password = None):
        if user == None or password == None:
            # (mis)use dbcredentials to read user/pass from disk
            from lofar.common import dbcredentials
            dbc = dbcredentials.DBCredentials()
            creds = dbc.get('MoM_site' if isProductionEnvironment() else 'MoM_site_test')
            user = creds.user
            password = creds.password

        self.mom_base_url = mom_base_url
        self.__user = user
        self.__password = password
        self.session = None

        self.__momURLlogin = self.mom_base_url + 'useradministration/user/systemlogin.do'
        self.__momUR_security_check = self.mom_base_url + 'useradministration/user/j_security_check'
        self.__momURLlogout = self.mom_base_url + 'useradministration/user/logout.do'

    def login(self):
        try:
            if self.session is not None:
                self.logout()

            logger.debug("logging in to MoM on url: %s", self.__momURLlogin)
            session = requests.session()
            r = session.get(self.__momURLlogin, verify=False)
            if 200 != r.status_code:
                raise Exception("Logging into MoM on %s failed: http return code = %s" % (self.__momURLlogin, r.status_code))

            r = session.post(self.__momUR_security_check, data={'j_username': self.__user, 'j_password': self.__password}, verify=False)
            if 200 != r.status_code:
                raise Exception("Logging into MoM on %s failed: http return code = %s" % (self.__momUR_security_check, r.status_code))

            logger.debug("logged in on MoM on url: %s", self.__momURLlogin)
            self.session = session
        except Exception as e:
            raise Exception("Logging into MoM on %s failed: %s" % (self.__momURLlogin, str(e)))

    def logout(self):
        try:
            if self.session is not None:
                logger.debug("logging out of MoM on url: %s", self.__momURLlogout)
                self.session.get(self.__momURLlogout, verify=False)
                self.session.close()
                self.session = None
                logger.debug("logged out of MoM on url: %s", self.__momURLlogout)
        except Exception as e:
            logger.warning("Logging out of MoM failed: " + str(e))

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

class SystemMoMClient(BaseMoMClient):
    def __init__(self, user=None, password=None):
        mom_base_url = 'https://lcs023.control.lofar:8443/' if isProductionEnvironment() else 'http://lofartest.control.lofar:8080/'
        super().__init__(mom_base_url, user, password)
        self.__momURLImportXML = self.mom_base_url + 'mom3/interface/importXML2.do'

    def setPipelineStatus(self, mom2id: int, status: str):
        try:
            logger.info("MoMClient.setPipelineStatus mom2id:%s status:%s", mom2id, status)

            self.login()

            xmlcontent = """<?xml version="1.0" encoding="UTF-8"?>
                              <lofar:pipeline mom2Id="%s" xmlns:lofar="http://www.astron.nl/MoM2-Lofar" xmlns:mom2="http://www.astron.nl/MoM2">
                                <currentStatus>
                                    <mom2:%sStatus/>
                                </currentStatus>
                            </lofar:pipeline>""" % (mom2id, status)

            # sanitize, make compact
            xmlcontent = xmlcontent.replace('\n', ' ')
            while '  ' in xmlcontent:
                xmlcontent = xmlcontent.replace('  ', ' ')

            params = {"command": "importxml2", "xmlcontent": xmlcontent}
            for i in range(3):
                response = self.session.post(self.__momURLImportXML, params=params)
                result = response.text

                # sanitize, make compact
                result = result.replace('\n', ' ')
                while '  ' in result:
                    result = result.replace('  ', ' ')

                if response.status_code == 200 and '<error>' not in result:
                    continue
                else:
                    logger.error("MoMClient.setPipelineStatus mom2id:%s status:%s failed: %s", mom2id, status, result)
                    sleep(1)

        except Exception as e:
            self.logout()
            raise Exception("MoMClient.setPipelineStatus mom2id:%s status:%s failed: %s" %(mom2id, status, e))

        if response.status_code != 200 or '<error>' in result:
            raise Exception("Could not set pipeline status mom2id:%s status:%s response: %s" % (mom2id, status, result))

if __name__ == '__main__':
    mc = SystemMoMClient()
    mc.setPipelineStatus(959395, 'opened')