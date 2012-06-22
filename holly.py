#!/usr/bin/env python
import fcntl
import json
import time
import sys
import util
import events
import commands
import traceback
import sys
import gevent
import config
from gevent import socket, monkey

monkey.patch_socket()

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
    s = connect(config.BACKEND)
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
        try:
          j = json.loads(line, encoding="iso-8859-1")
        except ValueError:
          LOG("line: " + repr(line))
          traceback.print_exc()
          continue

        gevent.spawn(process_line, irc, j["type"], j.get("data"))
      
    irc.socket = None
    LOG("disconnected, retrying in 5s...")
    time.sleep(5)

if __name__ == "__main__":
  with open(".lock", "w") as f:
    try:
      fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
      LOG("already running, exiting...")
      sys.exit(1)
    try:  
      main()
    finally:
     fcntl.lockf(f, fcntl.LOCK_UN)
