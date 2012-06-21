import util
import sqlite3

class DB(object):
  def __init__(self, name):
    self.d = sqlite3.connect(util.data_file(name) + ".sqlite", isolation_level=None)
    self.c = self.d.cursor()
    try:
      self.c.execute("CREATE TABLE store (key PRIMARY KEY, value);")
    except sqlite3.OperationalError:
      pass

  def __setitem__(self, key, value):
    self.c.execute("REPLACE INTO store (key, value) VALUES (?, ?)", (key, value))

  def __getitem__(self, key):
    self.c.execute("SELECT value FROM store WHERE key = ?", (key, ))
    row = self.c.fetchone()
    if row is None:
      raise KeyError(key)
    return row[0]

  def get(self, key, default=None):
    try:
      return self[key]
    except KeyError:
      return default

  def __contains__(self, key):
    try:
      self[key]
      return True
    except KeyError:
      return False

  def __delitem__(self, key):
    self.c.execute("DELETE FROM store WHERE key = ?", (key, ))
