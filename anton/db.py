import util
import sqlite3


class DB(object):
    def __init__(self, name):
        self.d = sqlite3.connect(util.data_file(name) + ".sqlite", isolation_level=None)

        c = self.d.cursor()
        try:
            c.execute("CREATE TABLE store (key PRIMARY KEY, value);")
        except sqlite3.OperationalError:
            pass
        finally:
            c.close()

    def __setitem__(self, key, value):
        c = self.d.cursor()
        try:
            c.execute("REPLACE INTO store (key, value) VALUES (?, ?)", (key, value))
        finally:
            c.close()

    def __getitem__(self, key):
        c = self.d.cursor()
        try:
            c.execute("SELECT value FROM store WHERE key = ?", (key, ))
            row = c.fetchone()
            if row is None:
                raise KeyError(key)
            return row[0]
        finally:
            c.close()

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
        c = self.d.cursor()
        try:
            c.execute("DELETE FROM store WHERE key = ?", (key, ))
        finally:
            c.close()

    def __iter__(self):
        return (k for k, _ in self.iteritems())

    def items(self):
        return dict(self.iteritems())

    def iteritems(self):
        c = self.d.cursor()
        try:
            c.execute("SELECT key, value FROM store")
            row = c.fetchone()
            while row is not None:
                yield row[0], row[1]
                row = c.fetchone()
        finally:
            c.close()


class LowercaseDB(DB):
    def __init__(self, *args, **kwargs): super(LowercaseDB, self).__init__(*args, **kwargs)

    def __t(self, key):
        return key.lower()

    def __getitem__(self, key):
        return super(LowercaseDB, self).__getitem__(self.__t(key))

    def get(self, key, default=None):
        return super(LowercaseDB, self).get(self.__t(key), default)

    def __contains__(self, key):
        return super(LowercaseDB, self).__contains__(self.__t(key))

    def __setitem__(self, key, value):
        super(LowercaseDB, self).__setitem__(self.__t(key), value)

    def __delitem__(self, key):
        super(LowercaseDB, self).__delitem__(self.__t(key))

    def items(self):
        return super(LowercaseDB, self).items()

    def iteritems(self):
        return super(LowercaseDB, self).iteritems()

    def __iter__(self):
        return super(LowercaseDB, self).__iter__()
