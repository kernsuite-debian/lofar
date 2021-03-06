
import os
import errno
import unittest
import shutil
import numpy
import tempfile
import xml.dom.minidom as xml
from unittest import mock

from lofarpipe.support.loggingdecorators import xml_node, duration, mail_log_on_exception
from lofar.common.defaultmailaddresses import PipelineEmailConfig
from lofarpipe.support.xmllogging import get_child, get_active_stack
#imports from fixture:


class loggingdecoratorsTest(unittest.TestCase):
    def __init__(self, arg):
        super(loggingdecoratorsTest, self).__init__(arg)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_xml_node_single_depth_timing_logging(self):
        """
        Test single nested duration logging
        Output xml is compared as is.
        """
        class Test(object):
            @xml_node
            def test(self):
                pass

        an_object = Test()
        an_object.test()

        #calling a decorated function should result in a active_stack node on the 
        # class. After finishing it should have the duration in there
        target_xml = '<active_stack Name="Test" type="active_stack"><active_stack/><test duration="0.0"/></active_stack>'

        self.assertTrue(float(get_child(
            an_object.active_stack, "test").getAttribute("duration")) <= 0.1,
            "The created active stack did not add the duration information")

    def test_xml_node_nested_timing_logging(self):
        """
        Test nested logging. The duration is variable. Test existance of 
        duration attribute and test that size of the created xml log is small.
        """
        class Test(object):
            @xml_node
            def test(self):
                pass

            @xml_node
            def test2(self):
                self.test()

        an_object = Test()
        an_object.test2()

        #calling a decorated function should result in a active_stack node on the 
        # class. After finishing it should have the duration in there
        target_xml = '<active_stack Name="Test" type="active_stack"><active_stack/><test duration="0.0"/></active_stack>'
        child2 = get_child(an_object.active_stack, "test2")
        child1 = get_child(child2, "test")
        self.assertTrue(float(child1.getAttribute("duration")) < 0.1,
                        "The duration was to large for the size of the test function")
        self.assertTrue(float(child2.getAttribute("duration")) < 0.1,
                        "The duration was to large for the size of the test function")

    def test_xml_node_return_value(self):
        """
        assure that the return value of the decorated function is still correct
        """
        class Test(object):
            @xml_node
            def test(self):
                return "a value"

        an_object = Test()
        return_value = an_object.test()

        self.assertTrue(return_value == "a value" ,
                        "The decorated function did not return the actual function return value ")

    def test_duration_context_manager(self):
        """
        Test that on entering the context with self the containing object
        pointer is added. It should also continue to exist after leaving the
        context
        
        """
        class tester(object):
            def __init__(self):
                pass

            def test(self):
                if get_active_stack(tester) is not None:
                    print("An active stack should only exist when added explicitly")
                    return False

                with duration(self, "a name") as context_object:
                    active_stack = get_active_stack(self)
                    # We should have an active stack in the context
                    if active_stack is None:
                        print("In duration context the active stack should be added.")
                        return False

                    if not get_child(
                        active_stack, "active_stack").hasChildNodes():
                        print("in the context the active_stack should at least contain one entry")
                        return False
                    # Now leave the  context

                if get_child(
                        active_stack, "active_stack").hasChildNodes():
                        print("After the context the active stack should be left")
                        # There is stil an entry in the active stack
                        return False

                return True

        test_object = tester()
        self.assertTrue(test_object.test(), "The duration context returned with False")

    @mock.patch('smtplib.SMTP')
    def test_mail_log_on_exception_raises_original_exception_of_decorated_function(self, smtpmock):

        class OriginalException(Exception):
            def __init__(self, message):
                self.message = message

        class Test(object):
            @mail_log_on_exception
            def test(self):
                raise OriginalException("This should be raised to the caller!")

        an_object = Test()

        with self.assertRaises(OriginalException):
            an_object.test()

    @mock.patch('lofarpipe.support.loggingdecorators.PipelineEmailConfig') # ! not: @mock.patch('lofar.common.defaultmailaddresses.PipelineEmailConfig')
    @mock.patch('smtplib.SMTP')
    def test_mail_log_on_exception_mails_with_correct_default_addresses_when_configuration_init_fails(self, smtpmock, pecmock):

        expected_server = "smtp.lofar.eu"
        expected_from = "noreply@lofar.eu"
        expected_to = ["sos@astron.nl"]

        pecmock.side_effect = Exception('This PipelineEmailConfig init failed...')

        class Test(object):
            @mail_log_on_exception
            def test(self):
                raise Exception("This should trigger an email")

        try:
            Test().test()
        except:
            pass

        pecmock.assert_called_once()

        smtpmock.assert_called_with(expected_server)

        smtpinstance = smtpmock.return_value

        self.assertTrue(smtpinstance.sendmail.called)
        self.assertEqual(expected_from, smtpinstance.sendmail.call_args[0][0])
        self.assertEqual(expected_to, smtpinstance.sendmail.call_args[0][1])

    @mock.patch('lofarpipe.support.loggingdecorators.PipelineEmailConfig')  # ! not: @mock.patch('lofar.common.defaultmailaddresses.PipelineEmailConfig')
    @mock.patch('smtplib.SMTP')
    def test_mail_log_on_exception_mails_with_correct_default_addresses_when_configuration_get_fails(self, smtpmock, pecmock):

        expected_server = "smtp.lofar.eu"
        expected_from = "noreply@lofar.eu"
        expected_to = ["sos@astron.nl"]

        # init a PipelineEmailConfig with an existing but empty config file so it does not fail on init, but raises an exception on access:
        # (mocking out the PipelineEmailConfig and adding a side_effect to its get() breaks the smtpmock for some reason)
        f = tempfile.NamedTemporaryFile()
        f.write(b""" """)
        f.flush()
        pecmock.return_value = PipelineEmailConfig(filepatterns=[f.name])

        class Test(object):
            @mail_log_on_exception
            def test(self):
                raise Exception("This should trigger an email")

        try:
            Test().test()
        except:
            pass

        pecmock.assert_called_once()

        smtpmock.assert_called_with(expected_server)

        smtpinstance = smtpmock.return_value

        self.assertTrue(smtpinstance.sendmail.called)
        self.assertEqual(expected_from, smtpinstance.sendmail.call_args[0][0])
        self.assertEqual(expected_to, smtpinstance.sendmail.call_args[0][1])


    @mock.patch('lofarpipe.support.loggingdecorators.PipelineEmailConfig')  # ! not: @mock.patch('lofar.common.defaultmailaddresses.PipelineEmailConfig')
    @mock.patch('smtplib.SMTP')
    def test_mail_log_on_exception_mails_with_correct_addresses_from_configuration_file(self, smtpmock, pecmock):

        expected_server = "smtp.lofar.eu"
        expected_from = "customized@astron.nl"
        expected_to = ["sos@astron.nl"]

        # init a PipelineEmailConfig with an existing but empty config file so it does not fail on init, but raises an exception on access:
        # (mocking out the PipelineEmailConfig and adding a side_effect to its get() breaks the smtpmock for some reason)
        f = tempfile.NamedTemporaryFile()
        f.write(b"""
[Pipeline]
error-sender = customized@astron.nl
""")
        f.flush()
        pecmock.return_value = PipelineEmailConfig(filepatterns=[f.name])

        class Test(object):
            @mail_log_on_exception
            def test(self):
                raise Exception("This should trigger an email")

        try:
            Test().test()
        except:
            pass

        pecmock.assert_called_once()

        smtpmock.assert_called_with(expected_server)

        smtpinstance = smtpmock.return_value

        self.assertTrue(smtpinstance.sendmail.called)
        self.assertEqual(expected_from, smtpinstance.sendmail.call_args[0][0])
        self.assertEqual(expected_to, smtpinstance.sendmail.call_args[0][1])


    @mock.patch('smtplib.SMTP')
    def test_mail_log_on_exception_does_not_mail_when_no_exception_raised(self, smtpmock):

        class Test(object):
            @mail_log_on_exception
            def test(self):
                return 0

        Test().test()

        instance = smtpmock.return_value
        self.assertFalse(instance.sendmail.called)


def main():
  unittest.main()

if __name__ == "__main__":
  # run all tests
  import sys
  main()
