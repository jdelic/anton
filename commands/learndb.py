import match
import commands
import anydbm
import util
import shelve
import dumbdbm
import db
import events

DB = db.DB("learndb")

@match.command(["!add", "++"])
def add(callback, key, value):
  if key[0] == "\"":
    v = ("%s %s" % (key[1:], value)).split("\" ", 1)
    if len(v) < 2:
      return "bad quoted data."
    key, value = v

  DB[key] = value
  return "got it!"

@match.command("--")
def remove(callback, key):
  if not key in DB:
    return "doesn't exist!"

  del DB[key]
  return "deleted %s" % key

def lookup(key, follow=True):
  value = DB.get(key)
  if value is None:
    return None

  if not follow:
    return value

  stack = [key]
  while True:
    if not value.startswith("@link "):
      return value

    new_key = value[6:]
    if new_key in stack:
      return "error: @link loop at %s (stack: %s)" % (key, repr(stack))
    stack.append(new_key)

    value = DB.get(new_key)
    if value is None:
      return "error: @link broken at %s (stack: %s)" % (key, repr(stack))

@match.command("holly:")
def query_bot(callback, key):
  value = lookup(key)
  if value is None:
    return commands.CONTINUE

  return value

@match.command("??")
def query(callback, key):
  value = lookup(key)
  if value is None:
    return "doesn't exist"

  return value

@match.command("?!")
def query(callback, key):
  value = lookup(key, follow=False)
  if value is None:
    return "doesn't exist"

  return value

@events.register("join")
def on_join(type, irc, obj):
  nick = obj["source"]["nick"]
  value = lookup(nick)
  if value is None:
    return

  irc.chanmsg(obj["channel"], "[%s] %s" % (nick, value))
