import commands

def return_callback(callback, result):
  if result is commands.CONTINUE:
    return result

  if result is None or result is commands.STOP:
    pass
  else:
    callback(result)
  return commands.STOP

def re(r):
  def decorate(fn):
    def new_fn(callback, message):
      m = r.match(message)
      if not m:
        return commands.CONTINUE

      return return_callback(callback, fn(callback, m))

    commands.register(new_fn)
    return new_fn

  return decorate

def command(name, args=-1):
  if isinstance(name, basestring):
    names = set([name])
  else:
    names = set(name)

  def decorate(fn):
    if args == -1:
      args2 = fn.func_code.co_argcount - 1
    else:
      args2 = args

    def new_fn(callback, message):
      tokens = message.split(" ", args2)
      if not tokens[0] in names:
        return commands.CONTINUE

      if args2 > len(tokens) - 1:
        callback("incorrect number of args for command: " + tokens[0])
        return commands.STOP

      return return_callback(callback, fn(callback, *tokens[1:]))

    commands.register(new_fn)
    return new_fn

  return decorate

def all(fn):
  def decorate(callback, message):
    return return_callback(callback, fn(callback, message))

  commands.register(decorate)
  return decorate
