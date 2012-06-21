import events
import traceback
STOP, CONTINUE = True, False

COMMANDS = []

def register(fn):
  COMMANDS.append(fn)

@events.register("chanmsg")
def chanmsg_handler(type, irc, obj):
  callback = lambda x: irc.chanmsg(obj["channel"], x)

  try:
    for command in COMMANDS:
      r = command(callback, obj["message"])
      if r == STOP:
        break
  except Exception, e:
    traceback.print_exc()
    callback("exception occured:")
    callback(traceback.format_exc())

import commands.learndb
import commands.thanks
import commands.urban_dictionary
import commands.google
