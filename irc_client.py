import socket
import util
import json
import events
import gevent
import config
import traceback
import time

from log import *

def connect(addr):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(addr)
  s.send("USER %s %s %s :%s\r\n" % (config.BOT_USERNAME, "wibble", "wibble", config.BOT_REALNAME))
  s.send("NICK %s\r\n" % config.BOT_NICKNAME)
  return s

class IRC(object):
  def write(self, message):
    self.socket.send("%s\r\n" % message.encode("utf8"))

  def chanmsg(self, channel, message):
    self.split_send(lambda message: self.write("PRIVMSG %s :%s" % (channel, message)), message)

  def privnotice(self, target, message):
    self.split_send(lambda message: self.write("NOTICE %s :%s" % (target, message)), message)

  def wallusers(self, message):
    pass
    self.split_send(lambda message: self.write("wallusers", {"message": message}), message)

  def wallops(self, message):
    pass
#    self.split_send(lambda message: self.write("wallops", {"message": message}), message)

  @classmethod
  def split_send(cls, fn, data):
    split_data = []
    for x in [data] if isinstance(data, basestring) else data:
      split_data.extend(x.replace("\r", "").split("\n"))

    for x in util.split_lines(split_data):
      fn(util.decode_irc(x, redecode=False))
    return

def parse_line(s):
  s = s[:-1]
  prefix = ""
  trailing = []
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

def to_source(prefix):
  source = {}
  source["nick"] = prefix.split("!")[0]
  source["ident"] = prefix.split("@")[0].split("!")[1]
  source["hostname"] = prefix.split("@")[1]
  return source

def process_line(irc, type, obj):
  print irc, type, obj
  if type == "PING":
    irc.write("PONG " + obj["args"][0])
  elif type == "PRIVMSG":
    source = to_source(obj["prefix"])
    if obj["args"][0][0] == "#":
      events.fire("chanmsg", irc, {"source": source, "channel": obj["args"][0], "message": obj["args"][1]})
    else:      
      events.fire("privmsg", irc, {"source": source, "message": obj["args"][1]})
  elif type == "JOIN":
    events.fire("join", irc, {"source": to_source(obj["prefix"]), "channel": obj["args"][0]})
  elif type == "001":
    for channel in config.BOT_CHANNELS:
      irc.write("JOIN %s" % channel)
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

      buf+=line
      lines = buf.split("\n")
      buf = lines.pop(-1)

      for line in lines:
        try:
          j = parse_line(line)
        except ValueError:
          LOG("line: " + repr(line))
          traceback.print_exc()
          continue
        print j

        gevent.spawn(process_line, irc, j["type"], j.get("data"))

    irc.socket = None
    LOG("disconnected, retrying in 5s...")
    time.sleep(5)

