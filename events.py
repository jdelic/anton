EVENTS = {}
STOP, CONTINUE = True, False

def register(type):
  def decorate(fn):
    EVENTS.setdefault(type, []).append(fn)
    return fn

  return decorate

def fire(type, context, obj):
  for x in EVENTS.get(type, []):
    x(type, context, obj)
