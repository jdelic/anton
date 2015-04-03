# -* coding: utf-8 *-
import logging

import re
import mock
import unittest
import socket
import gevent.monkey
import gevent.server
from anton import commands, irc_client


_log = logging.getLogger(__name__)


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


class TestIRCServer(gevent.server.StreamServer):
    def __init__(self, *args, **kwargs):
        super(TestIRCServer, self).__init__(*args, **kwargs)
        self.max_receive = kwargs.get("max_receive", 1)
        self.received = []
        self._message = ""

    def handle(self, sock, address):
        gevent.spawn(self.read, sock)
        gevent.spawn(self.write, sock)

    def read(self, sock):
        recv_messagecount = 0
        while recv_messagecount < self.max_receive:
            recv_messagecount = recv_messagecount + 1
            _log.debug("wait server %s", sock)
            line = sock.recv(8192)
            if line:
                self.received.append(line)
                _log.debug("server received: %s", line)
            else:
                break

    def write(self, socket):
        if self._message:
            socket.sendall(self._message)
            self._message = ""

    def queuemessage(self, msg):
        self._message = msg


class TestIRCProtocol(unittest.TestCase):
    """
    This sends test IRC protocol messages through the protocol parser anton.irc_client.IRC,
    the events infrastructure in anton.events, the IRC event receivers in anton.commands and
    then checks that these invoke registered anton.commands handlers.
    """

    chanmsg = ":TheFonz!~fonz@eastmeadow/ PRIVMSG #test :Eeey!\r\n"
    privmsg = ":TheFonz!~fonz@eastmeadow/ PRIVMSG anton :Eeey!\r\n"

    @classmethod
    def setUpClass(cls):
        gevent.monkey.patch_socket()

    @classmethod
    def tearDownClass(cls):
        # remove monkey patching
        reload(socket)

    def setUp(self):
        self.irc_server = TestIRCServer(('127.0.0.1', 0))
        self.irc_server.start()
        self.irc_client = irc_client.IRC(max_reconnects=1, max_messages=1)

        import anton
        anton.config.BACKEND = ("127.0.0.1", self.irc_server.server_port)

        self.irc_client.chanmsg = mock.Mock()
        self.irc_client.privnotice = mock.Mock()
        self.irc_client.start()

    def tearDown(self):
        commands.COMMANDS = []  # remove each registered commands so they don'r influence other tests
        self.irc_client.kill()
        self.irc_server.stop()

    def test_parseline_crlf(self):
        x = self.irc_client.parse_line(TestIRCProtocol.chanmsg)
        self.assertDictEqual(x, {
            "type": "PRIVMSG",
            "data": {
                "prefix": "TheFonz!~fonz@eastmeadow/",
                "args": ["#test", "Eeey!"]
            }
        })

    def test_parseline_lf(self):
        x = self.irc_client.parse_line(TestIRCProtocol.chanmsg.rstrip("\r\n") + "\n")
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

        self.irc_server.queuemessage(TestIRCProtocol.chanmsg)
        self.irc_client.join()
        self.irc_client.chanmsg.assert_called_once_with("#test", "thumbsup")

    def test_privmsg(self):
        @commands.register("Eeey!")
        def testhandler(callback):
            return "thumbsup"

        self.irc_server.queuemessage(TestIRCProtocol.privmsg)
        self.irc_client.join()
        self.irc_client.privnotice.assert_called_once_with("TheFonz", "thumbsup")
