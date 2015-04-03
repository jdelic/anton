# -* coding: utf-8 *-

import re
import mock
import unittest
from anton import commands, irc_client


class TestCommands(unittest.TestCase):
    """
    This tests all of the commands.register match strategies
    """
    def setUp(self):
        self._returned = None

    def tearDown(self):
        commands.COMMANDS = []  # remove each registered commands so they don'r influence other tests

    def _testcallback(self, value):
        self._returned = value

    def test_regex_matcher(self):
        def testhandler(callback, message):
            return "blah"

        handler = commands.register(re.compile(".*?wibble.*"))(testhandler)
        handler(self._testcallback, "xxxwibblexxx")
        self.assertEqual(self._returned, "blah")

    def test_command_matcher(self):
        def testhandler(callback, argument):
            return argument

        handler = commands.register(["!boink", "!blink"])(testhandler)
        handler(self._testcallback, u"!boink plönk")
        self.assertEqual(self._returned, u"plönk")
        handler(self._testcallback, u"!blink plänk")
        self.assertEqual(self._returned, u"plänk")
        handler(self._testcallback, u"!wibble stink")
        self.assertNotEqual(self._returned, u"stink")

        handler = commands.register("%single")(testhandler)
        handler(self._testcallback, "%single string")
        self.assertEqual(self._returned, "string")

    def test_all_matcher(self):
        def testhandler(callback, arg):
            return "boink%s" % arg

        handler = commands.register()(testhandler)
        handler(self._testcallback, "1")
        self.assertEqual(self._returned, "boink1")
        handler(self._testcallback, "2")
        self.assertEqual(self._returned, "boink2")


class TestIRCProtocol(unittest.TestCase):
    """
    This sends test IRC protocol messages through the protocol parser anton.irc_client.IRC,
    the events infrastructure in anton.events, the IRC event receivers in anton.commands and
    then checks that these invoke registered anton.commands handlers.
    """

    chanmsg = ":TheFonz!~fonz@eastmeadow/ PRIVMSG #test :Eeey!\n"
    privmsg = ":TheFonz!~fonz@eastmeadow/ PRIVMSG anton :Eeey!\n"

    def setUp(self):
        self.irc = irc_client.IRC()
        self.irc._socket = mock.Mock()
        self.irc.chanmsg = mock.Mock()
        self.irc.privnotice = mock.Mock()

    def tearDown(self):
        commands.COMMANDS = []  # remove each registered commands so they don'r influence other tests

    def test_parseline(self):
        x = self.irc.parse_line(TestIRCProtocol.chanmsg)
        self.assertDictEqual(x, {
            "type": "PRIVMSG",
            "data": {
                "prefix": "TheFonz!~fonz@eastmeadow/",
                "args": ["#test", "Eeey!"]
            }
        })

    def test_chanmsg(self):
        @commands.register("Eeey!")
        def testhandler(callback):
            return "thumbsup"

        x = self.irc.parse_line(TestIRCProtocol.chanmsg)
        self.irc.process_line(x["type"], x["data"])
        self.irc.chanmsg.assert_called_once_with("#test", "thumbsup")

    def test_privmsg(self):
        @commands.register("Eeey!")
        def testhandler(callback):
            return "thumbsup"

        x = self.irc.parse_line(TestIRCProtocol.privmsg)
        self.irc.process_line(x["type"], x["data"])
        self.irc.privnotice.assert_called_once_with("TheFonz", "thumbsup")
