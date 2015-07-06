from _ssl import SSLError
import logging
import os
import socket
import ssl
import time
import events
import gevent
import gevent.queue
import gevent.event

from anton import util
from anton import config


_log = logging.getLogger(__name__)


class IRC(object):
    def __init__(self, max_reconnects=0, max_messages=0):
        """
        :param max_reconnects: number of reconnection attempts (0 means unlimited [default])
        :param max_messages:  number of messages to process per connection attempt (0 means unlimited [default])
        :return:
        """
        super(IRC, self).__init__()
        self._socket = None
        self.max_reconnects = max_reconnects
        self.max_messages = max_messages
        self.current_reconnects = 0
        self.current_messagecount = 0
        self._message_queue = gevent.queue.Queue()
        self.reader_greenlet = None
        self.writer_greenlet = None
        self._disconnect_event = gevent.event.Event()
        self._shutdown_event = gevent.event.Event()
        self.started = False
        self.stopped = False
        self.last_ping = 0

    def connect(self, addr):
        """
        Connects the IRC client to a server and creates reader and writer threads which process messages and
        send queued IRC messages back to the server.
        """
        self._disconnect_event.clear()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if config.IRC_USESSL in ["yes", "true", "1"]:
            self._socket = ssl.wrap_socket(self._socket)

        try:
            self._socket.connect(addr)
        except SSLError as e:
            _log.debug("Connecting to server raised %s", e)
            self.disconnect()
            return
        except socket.error as e:
            _log.debug("Sending to server raised %s", e)
            self.disconnect()
            return

        if config.BOT_PASSWORD:
            self._socket.send("PASS %s\r\n" % config.BOT_PASSWORD)

        self._socket.send("USER %s %s %s :%s\r\n" % (config.BOT_USERNAME, "wibble", "wibble", config.BOT_REALNAME))
        self._socket.send("NICK %s\r\n" % config.BOT_NICKNAME)

        # empty the queue when we start working to make sure we don't process stale StopIterations
        self._message_queue.empty()
        self.reader_greenlet = gevent.spawn(self._reader)
        self.writer_greenlet = gevent.spawn(self._writer)

        self.last_ping = time.time()  # we have just connected, so let's pretend we just got pinged

    def _reader(self):
        buf = ""
        while self.allow_message_processing():
            self.current_messagecount = self.current_messagecount + 1

            line = None
            try:
                _log.debug("listening %s", self.reader_greenlet)
                line = self._socket.recv(8192)
            except socket.error as e:
                # we swallow the socket.error raised by gevent.socket.cancel_wait_ex here because it's perfectly
                # normal for another Greenlet to close our underlying socket while we were blocked in recv().
                _log.debug("socket.error %s %s %s", os.strerror(e.errno), e, self.reader_greenlet)
                self.disconnect()
                break

            if not line:
                _log.debug("empty response received from IRC socket '%s' %s", line, self.reader_greenlet)
                self.disconnect()
                break

            buf += line
            lines = buf.split("\n")
            buf = lines.pop(-1)

            for line in lines:
                try:
                    j = self.parse_line(line)
                except ValueError, e:
                    _log.error("line: " + repr(line), e)
                    continue
                _log.debug(j)

                gevent.spawn(self.process_line, j["type"], j.get("data"))

        _log.debug("Message count: %s/%s %s", self.current_messagecount, self.max_messages, self.reader_greenlet)
        self.current_messagecount = 0

    def _writer(self):
        while self._message_queue.peek():
            msg = self._message_queue.get()

            if msg is StopIteration:
                _log.debug("Writer Greenlet exiting on StopIteration")
                # TODO: should this disconnect?
                return

            self.split_send(lambda m: self.write("%s %s :%s" % (msg['type'], msg['target'], m)), msg['message'])

    def write(self, message):
        try:
            self._socket.send("%s\r\n" % message.encode("utf8"))
        except SSLError as e:
            _log.debug("Sending to server raised %s", e)
            self.disconnect()
        except socket.error as e:
            _log.debug("Sending to server raised %s", e)
            self.disconnect()

    def chanmsg(self, channel, message):
        self._message_queue.put({
            'type': 'PRIVMSG',
            'target': channel,
            'message': message,
        })

    def privnotice(self, target, message):
        self._message_queue.put({
            'type': 'NOTICE',
            'target': target,
            'message': message,
        })

    def wallusers(self, message):
        # self.split_send(lambda message: self.write("wallusers", {"message": message}), message)
        pass

    def wallops(self, message):
        # self.split_send(lambda message: self.write("wallops", {"message": message}), message)
        pass

    @staticmethod
    def split_send(fn, data):
        split_data = []
        for x in [data] if isinstance(data, basestring) else data:
            split_data.extend(x.replace("\r", "").split("\n"))

        for x in util.split_lines(split_data):
            fn(util.decode_irc(x, redecode=False))

    @staticmethod
    def parse_line(s):
        s = s.rstrip("\r\n")
        prefix = ""
        if not s:
            raise Exception("Empty line.")
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)

        return {"type": command, "data": {"prefix": prefix, "args": args}}

    @staticmethod
    def to_source(prefix):
        ident = ""
        hostname = ""
        if "@" in prefix and "!" in prefix:
            ident = prefix.split("@")[0].split("!")[1]
        if "@" in prefix:
            hostname = prefix.split("@")[1]

        source = {
            "nick": prefix.split("!")[0],
            "ident": ident,
            "hostname": hostname
        }
        return source

    def process_line(self, msgtype, obj):
        if msgtype == "PING":
            self.last_ping = time.time()
            self.write("PONG " + obj["args"][0])
        elif msgtype == "PRIVMSG":
            source = self.to_source(obj["prefix"])
            if obj["args"][0][0] == "#":
                events.fire("chanmsg", self, {"source": source, "channel": obj["args"][0], "message": obj["args"][1]})
            else:
                events.fire("privmsg", self, {"source": source, "message": obj["args"][1]})
        elif msgtype == "JOIN":
            events.fire("join", self, {"source": self.to_source(obj["prefix"]), "channel": obj["args"][0]})
        elif msgtype == "001":
            for channel in config.BOT_CHANNELS.split(','):
                self.write("JOIN %s" % channel.strip())
        else:
            _log.warning("bad command type: %r: %r" % (type, obj))

    def allow_reconnect(self):
        if self.max_reconnects == 0 and not self._shutdown_event.is_set():
            return True
        elif self.current_reconnects < self.max_reconnects and not self._shutdown_event.is_set():
            return True
        else:
            self._shutdown_event.set()
            return False

    def allow_message_processing(self):
        if self.max_messages == 0 and not self._disconnect_event.is_set():
            return True
        elif self.current_messagecount < self.max_messages and not self._disconnect_event.is_set():
            return True
        else:
            self._disconnect_event.set()
            return False

    def start(self):
        """
        Starts the client with a watcher thread which will reconnect the client after a 5 second wait
        when it gets disconnected (up to self.max_reconnects) or receives the maximum messages allowed
        before it must reconnect (self.max_messages).

        :return: The watcher Greenlet that you can gevent.wait() on, for example.
        """
        if self.started:
            return

        self.started = True

        def _watcher():
            while self.allow_reconnect():
                self.current_reconnects = self.current_reconnects + 1
                _log.info("connecting to %s:%s...", config.BACKEND[0], config.BACKEND[1])
                self.connect(config.BACKEND)
                _log.info("connected!")

                self.wallops("anton online")

                _log.debug("Entering inner loop with timeout %s", config.IRC_CONNECTIONCHECK_TIMEOUT)
                while not self._disconnect_event.wait(timeout=config.IRC_CONNECTIONCHECK_TIMEOUT):
                    t = time.time() - self.last_ping
                    if t > config.IRC_PING_RECONNECT_TIMEOUT:
                        # we haven't had a PING in a while... we should assume the connection is broken
                        _log.warning("PING timeout (%s > %s), reconnecting...", t, config.IRC_PING_RECONNECT_TIMEOUT)
                        self.disconnect()
                        break

                if self.allow_reconnect():
                    _log.info("disconnected, retrying in 5s...")
                    gevent.sleep(5)

            if self.current_reconnects >= self.max_reconnects:
                _log.warning("Maximum reconnection attempts reached (%s)", self.max_reconnects)

            if self._shutdown_event.is_set():
                _log.info("Shutting down...")

        return gevent.spawn(_watcher)

    def stop(self):
        """
        Disconnects the client from the server immediately and shuts it down (it won't reconnect after being stopped).
        """
        if self.stopped:
            return

        self.stopped = True
        self._shutdown_event.set()
        self.disconnect()

    def disconnect(self):
        self._disconnect_event.set()
        self._message_queue.put(StopIteration)
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except socket.error as e:
            # at this point the socket might already have been closed or gone stale, so this will sometimes
            # throw errors which are meaningless to us. Shutting down the socket here is about being a good citizen
            # and sending TCP FIN if we still can.
            _log.debug("Disconnecting from server raised %s", e)

    def run_eventloop(self, timeout=None):
        """
        You can call this method to block and run the IRC client until it disconnects. It's a helper method
        like gevent.baseserver.BaseServer.serve_forever, i.e. it will block until the client dies.
        """
        if not self.started:
            self.start()
        self._shutdown_event.wait(timeout=timeout)
