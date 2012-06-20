import util
import dumbdbm
import shelve

class DB(object):
  def __init__(self, name):
    self.d = dumbdbm.open(util.data_file(name))

  def __setitem__(self, key, value):
    self.d[self.t(key)] = self.t(value)
    self.d.sync()

  def __getitem__(self, key):
    return self.de(self.d[self.t(key)])

  def get(self, key, default=None):
    key = self.t(key)
    if not key in self.d:
      return default
    return self.de(self.d[key])

  def __contains__(self, key):
    return self.t(key) in self.d

  def __delitem__(self, key):
    del self.d[self.t(key)]
    self.d.sync()

  def t(self, value):
    return value.encode("utf8")

  def de(self, value):
    return value.decode("utf8")
