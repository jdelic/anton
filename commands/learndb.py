import match
import commands
import util
import db
import events

DB = db.LowercaseDB("learndb")

class BadQuotedDataException(Exception):
  pass

class LookupException(Exception):
  pass

def quote_parse(key, value):
  if key[0] == "\"":
    v = ("%s %s" % (key[1:], value)).split("\" ", 1)
    if len(v) < 2:
      raise BadQuotedDataException
    key, value = v
  return key, value

@match.command(["!add", "++"])
def add(callback, key, value):
  try:
    key, value = quote_parse(key, value)
  except BadQuotedDataException:
    return "bad quoted data"

  DB[key] = value
  return "got it!"

@match.command("--")
def remove(callback, key):
  if not key in DB:
    return "doesn't exist!"

  del DB[key]
  return "deleted"

def lookup(key, follow=True, return_key=False):
  value = DB.get(key)
  if value is None:
    raise KeyError

  if not follow:
    if return_key:
      return key
    return value

  stack = [key]
  while True:
    if not value.startswith("@link "):
      if return_key:
        return key
      return value

    new_key = value[6:]
    if new_key in stack:
      raise LookupException("error: @link loop at %s (stack: %s)" % (key, repr(stack)))
    stack.append(new_key)

    value = DB.get(new_key)
    if value is None:
      raise LookupException("error: @link broken at %s (stack: %s)" % (key, repr(stack)))

@match.command("holly:")
def query_bot(callback, key):
  try:
    value = lookup(key)
  except KeyError:
    return commands.CONTINUE
  except LookupException, e:
    return commands.CONTINUE

  return value

@match.command("??")
def query(callback, key):
  try:
    value = lookup(key)
  except KeyError:
    return "doesn't exist"
  except LookupException, e:
    return e.args[0]

  return value

@match.command("&&")
def query_no_follow(callback, key):
  try:
    value = lookup(key, follow=False)
  except KeyError:
    return "doesn't exist"
  except LookupException, e:
    return e.args[0]

  return value

@match.command("++a")
def append(callback, key, value):
  try:
    key, value = quote_parse(key, value)
  except BadQuotedDataException:
    return "bad quoted data"

  try:
    key = lookup(key, return_key=True)
  except KeyError:
    return "doesn't exist"
  except LookupException, e:
    return e.args[0]

  DB[key] = DB[key] + value
  return "done"

@events.register("join")
def on_join(type, irc, obj):
  nick = obj["source"]["nick"]

  try:
    value = lookup(nick)
  except KeyError:
    return

  irc.chanmsg(obj["channel"], "[%s] %s" % (nick, value))
