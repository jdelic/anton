import logging
import socket
import ssl
import events
import gevent

from anton import util
from anton import config


_log = logging.getLogger(__name__)


class IRC(gevent.Greenlet):
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

    def connect(self, addr):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if config.IRC_USESSL in ["yes", "true", "1"]:
            self._socket = ssl.wrap_socket(self._socket)

        self._socket.connect(addr)
        if config.BOT_PASSWORD:
            self._socket.send("PASS %s\r\n" % config.BOT_PASSWORD)

        self._socket.send("USER %s %s %s :%s\r\n" % (config.BOT_USERNAME, "wibble", "wibble", config.BOT_REALNAME))
        self._socket.send("NICK %s\r\n" % config.BOT_NICKNAME)
        return True

    def write(self, message):
        self._socket.send("%s\r\n" % message.encode("utf8"))

    def chanmsg(self, channel, message):
        self.split_send(lambda message: self.write("PRIVMSG %s :%s" % (channel, message)), message)

    def privnotice(self, target, message):
        self.split_send(lambda message: self.write("NOTICE %s :%s" % (target, message)), message)

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
        return

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
        source = {
            "nick": prefix.split("!")[0],
            "ident": prefix.split("@")[0].split("!")[1],
            "hostname": prefix.split("@")[1]
        }
        return source

    def process_line(self, type, obj):
        if type == "PING":
            self.write("PONG " + obj["args"][0])
        elif type == "PRIVMSG":
            source = self.to_source(obj["prefix"])
            if obj["args"][0][0] == "#":
                events.fire("chanmsg", self, {"source": source, "channel": obj["args"][0], "message": obj["args"][1]})
            else:
                events.fire("privmsg", self, {"source": source, "message": obj["args"][1]})
        elif type == "JOIN":
            events.fire("join", self, {"source": self.to_source(obj["prefix"]), "channel": obj["args"][0]})
        elif type == "001":
            for channel in config.BOT_CHANNELS.split(','):
                self.write("JOIN %s" % channel.strip())
        else:
            _log.warning("bad command type: %r: %r" % (type, obj))

    def allow_reconnect(self):
        if self.max_reconnects == 0:
            return True
        else:
            return self.current_reconnects < self.max_reconnects

    def allow_message_processing(self):
        if self.max_messages == 0:
            return True
        else:
            return self.current_messagecount < self.max_messages

    def _run(self):
        while self.allow_reconnect():
            self.current_reconnects = self.current_reconnects + 1
            _log.info("connecting to %s:%s..." % config.BACKEND)
            self.connect(config.BACKEND)
            _log.info("connected!")

            self.wallops("anton online")
            buf = ""
            while self.allow_message_processing():
                self.current_messagecount = self.current_messagecount + 1
                line = self._socket.recv(8192)
                if not line:
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

            _log.debug("Message count: %s", self.current_messagecount)
            if not self.allow_message_processing():
                _log.debug("Maximum number of messages per connection reached (%s)", self.max_messages)

            self.current_messagecount = 0
            self._socket.close()
            self._socket = None

            if self.allow_reconnect():
                _log.info("disconnected, retrying in 5s...")
                gevent.sleep(5)

        _log.warning("Maximum reconnection attempts reached (%s)", self.max_reconnects)
