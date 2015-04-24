# -* coding: utf-8 *-
import logging

import re
import unittest
import socket
import gevent.monkey
import gevent.server
import gevent.queue
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
    def __init__(self, checkfor, *args, **kwargs):
        self.received = []
        self._irc_message_queue = gevent.queue.Queue()
        self.checkfor = checkfor
        self.message_received = False
        super(TestIRCServer, self).__init__(*args, **kwargs)

    def handle(self, sock, address):
        gevent.spawn(self.read, sock)
        gevent.spawn(self.write, sock)

    def read(self, sock):
        filelike = sock.makefile()
        while True:
            line = filelike.readline()
            if line:
                _log.debug("Server received %s", line)
                self.received.append(line)
                if self.checkfor in line:
                    self.message_received = True
                    self.close()
                    break
            else:
                break

    def write(self, sock):
        while self._irc_message_queue.peek():
            msg = self._irc_message_queue.get()

            if msg is StopIteration:
                return

            sock.send(msg)

    def queuemessage(self, msg):
        self._irc_message_queue.put(msg)

    def close(self):
        super(TestIRCServer, self).close()
        self.queuemessage(StopIteration)


class TestIRCProtocol(unittest.TestCase):
    chanmsg = ":TheFonz!~fonz@eastmeadow/ PRIVMSG #test :Eeey!\r\n"
    privmsg = ":TheFonz!~fonz@eastmeadow/ PRIVMSG anton :Eeey!\r\n"

    def test_parseline_crlf(self):
        ircc = irc_client.IRC()
        x = ircc.parse_line(TestIRCProtocol.chanmsg)
        self.assertDictEqual(x, {
            "type": "PRIVMSG",
            "data": {
                "prefix": "TheFonz!~fonz@eastmeadow/",
                "args": ["#test", "Eeey!"]
            }
        })

    def test_parseline_lf(self):
        ircc = irc_client.IRC()
        x = ircc.parse_line(TestIRCProtocol.chanmsg.rstrip("\r\n") + "\n")
        self.assertDictEqual(x, {
            "type": "PRIVMSG",
            "data": {
                "prefix": "TheFonz!~fonz@eastmeadow/",
                "args": ["#test", "Eeey!"]
            }
        })


class TestIRCClient(unittest.TestCase):
    """
    This sends test IRC protocol messages through the protocol parser anton.irc_client.IRC,
    the events infrastructure in anton.events, the IRC event receivers in anton.commands and
    then checks that these invoke registered anton.commands handlers.
    """

    @classmethod
    def setUpClass(cls):
        gevent.monkey.patch_socket()

    @classmethod
    def tearDownClass(cls):
        # remove monkey patching
        reload(socket)

    @staticmethod
    def setup_irctest(check_for_string_sent, max_reconnects=0, max_messages=0):
        ircserver = TestIRCServer(check_for_string_sent, ('127.0.0.1', 0))
        ircserver.start()
        ircclient = irc_client.IRC(max_reconnects=max_reconnects, max_messages=max_messages)

        import anton
        anton.config.BACKEND = ("127.0.0.1", ircserver.server_port)
        ircclient.start()
        return ircserver, ircclient

    def tearDown(self):
        commands.COMMANDS = []  # remove all registered commands so they don't influence other tests

    def test_the_network_test(self):
        ircs, ircc = TestIRCClient.setup_irctest("thumbsup", 1, 3)

        @commands.register("Eeey!")
        def testhandler(callback):
            return "thumbsdown"

        ircs.queuemessage(TestIRCProtocol.chanmsg)
        gevent.wait(timeout=2)
        self.assertFalse(ircs.message_received)

    def test_chanmsg(self):
        ircs, ircc = TestIRCClient.setup_irctest("thumbsup", 1, 3)

        @commands.register("Eeey!")
        def testhandler(callback):
            return "thumbsup"

        ircs.queuemessage(TestIRCProtocol.chanmsg)
        gevent.wait(timeout=2)
        self.assertTrue(ircs.message_received)
        self.assertEqual(ircs.received[-1], "PRIVMSG #test :thumbsup\r\n")

    def test_privmsg(self):
        ircs, ircc = TestIRCClient.setup_irctest("thumbsup", 1, 3)

        @commands.register("Eeey!")
        def testhandler(callback):
            return "thumbsup"

        ircs.queuemessage(TestIRCProtocol.privmsg)
        gevent.wait(timeout=2)
        self.assertTrue(ircs.message_received)
        self.assertEqual(ircs.received[-1], "NOTICE TheFonz :thumbsup\r\n")

    def test_events(self):
        ircs, ircc = TestIRCClient.setup_irctest("thumbsup", 1, 3)

        def killafter1second():
            gevent.sleep(1)
            ircc.stop()
            ircs.close()

        gevent.spawn(killafter1second)
        gevent.sleep(1)
        try:
            ircc.reader_greenlet.get(timeout=2)
        except gevent.Timeout:
            self.fail("The reader greenlet hasn't closed shop after the stop event")

        try:
            ircc.writer_greenlet.get(timeout=2)
        except gevent.Timeout:
            self.fail("The writer greenlet hasn't closed shop after the stop event")

        gevent.wait(timeout=2)  # if anything else blocks, we find it here
