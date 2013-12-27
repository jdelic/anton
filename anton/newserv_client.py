import socket
import json
import events
import gevent
import traceback

from anton import config
from anton import util
from anton.log import *


def connect(addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    return s


class IRC(object):
    def write(self, type, obj):
        self.socket.send(json.dumps({"type": type, "data": obj}, ensure_ascii=False).encode("utf8") + "\n")

    def chanmsg(self, channel, message):
        self.split_send(lambda message: self.write("chanmsg", {"channel": channel, "message": message}), message)

    def privnotice(self, target, message):
        self.split_send(lambda message: self.write("privnotice", {"target": target, "message": message}), message)

    def wallusers(self, message):
        self.split_send(lambda message: self.write("wallusers", {"message": message}), message)

    def wallops(self, message):
        self.split_send(lambda message: self.write("wallops", {"message": message}), message)

    @classmethod
    def split_send(cls, fn, data):
        split_data = []
        for x in [data] if isinstance(data, basestring) else data:
            split_data.extend(x.replace("\r", "").split("\n"))

        for x in util.split_lines(split_data):
            fn(util.decode_irc(x, redecode=False))
        return


def process_line(irc, type, obj):
    if type == "chanmsg":
        obj["message"] = util.decode_irc(obj["message"])
        events.fire("chanmsg", irc, obj)
    elif type == "privmsg":
        obj["message"] = util.decode_irc(obj["message"])
        events.fire("privmsg", irc, obj)
    elif type == "join":
        events.fire("join", irc, obj)
    elif type == "startup":
        irc.write("join", {"channel": "#twilightzone"})
    else:
        LOG("bad command type: %r: %r" % (type, obj))


def irc_instance():
    return IRC()


def client(irc):
    while True:
        LOG("connecting...")
        s = connect(config.BACKEND)
        irc.socket = s

        LOG("connected!")

        irc.wallops("holly online")
        buf = ""
        while True:
            line = s.recv(8192)
            if not line:
                break

            buf += line
            lines = buf.split("\n")
            buf = lines.pop(-1)

            for line in lines:
                try:
                    j = json.loads(line, encoding="iso-8859-1", strict=False)
                except ValueError:
                    LOG("line: " + repr(line))
                    traceback.print_exc()
                    continue

                gevent.spawn(process_line, irc, j["type"], j.get("data"))

        irc.socket = None
        LOG("disconnected, retrying in 5s...")
        gevent.sleep(5)

