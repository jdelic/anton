#!/usr/bin/env python
BACKEND = "10.13.37.143", 5050

import json
import time
import sys
import util
from gevent import socket
import events
import commands
import traceback

def LOG(line):
  print >>sys.stderr, line

def connect(addr):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(addr)
  return s

class IRC(object):
  def write(self, type, obj):
    self.socket.send(json.dumps({"type": type, "data": obj}, ensure_ascii=False).encode("utf8") + "\n")

  def chanmsg(self, channel, message):
    fn = lambda message: self.write("chanmsg", {"channel": channel, "message": message})
    self.split_send(lambda message: self.write("chanmsg", {"channel": channel, "message": message}), message)

  @classmethod
  def split_send(cls, fn, data):
    split_data = []
    for x in [data] if isinstance(data, basestring) else data:
      split_data.extend(x.replace("\r", "").split("\n"))

    for x in util.split_lines(split_data):
      fn(x)
    return 

def process_line(irc, type, obj):
  if type == "chanmsg":
    obj["message"] = util.decode_irc(obj["message"])
    events.fire("chanmsg", irc, obj)
  elif type == "join":
    events.fire("join", irc, obj)
  elif type == "startup":
    irc.write("join", {"channel": "#twilightzone"})
  else:
    LOG("bad command type: %r: %r" % (type, obj))

def main():
  irc = IRC()

  while True:
    LOG("connecting...")
    s = connect(BACKEND)
    irc.socket = s

    LOG("connected!")

    buf = ""
    while True:
      line = s.recv(8192)
      if line is None:
        break

      buf+=line
      lines = buf.split("\n")
      buf = lines.pop(-1)

      for line in lines:
        LOG("line: " + repr(line))
        try:
          j = json.loads(line, encoding="iso-8859-1")
        except ValueError:
          traceback.print_exc()
          continue
        process_line(irc, j["type"], j.get("data"))
      
    irc.socket = None
    LOG("disconnected, retrying in 5s...")
    time.sleep(5)

if __name__ == "__main__":
  main()

