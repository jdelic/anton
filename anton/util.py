import os
import sys
import config
import codecs
import HTMLParser
import re


def split_lines(data, **kwargs):
    result = []
    for x in data:
        result.extend(split_line(x, **kwargs))
    return result


def import_module(modulename):
    try:
        __import__(modulename)
    except ImportError as e:
        raise

    return sys.modules[modulename]


def get_class_from_string(fqcn):
    try:
        modulename, classname = fqcn.rsplit('.', 1)
    except ValueError:
        raise Exception("Can't parse class name %s, it needs to be a fully qualified class name" % fqcn)

    module = import_module(modulename)

    try:
        clazz = getattr(module, classname)
    except AttributeError:
        raise Exception("Can't load class %s from module %s. Does it exist?" % (classname, modulename))

    return clazz


def split_line(data, split_at=400, force_split_at=350, separator="..."):
    result = []
    if len(data) < split_at:
        return [data]

    reversed = data[split_at::-1]
    reversed_last_space = reversed.find(" ")

    if reversed_last_space == -1:
        do_split_at = split_at
        forced = True
    else:
        last_space = len(reversed) - reversed_last_space - 1
        if last_space < force_split_at:
            do_split_at = split_at
            forced = True
        else:
            do_split_at = last_space
            forced = False

    offset = 0 if forced else 1
    component1, component2 = data[:do_split_at], data[do_split_at + offset:]

    if forced:
        format_string = "%s%s"
    else:
        format_string = "%s %s"

    next = split_line(component2, split_at=split_at, force_split_at=force_split_at, separator=separator)
    result = ["%s%s" % (component1, separator)]
    result.append(format_string % (separator, next[0]))
    result.extend(next[1:])

    return result


def data_file(value):
    return os.path.join(config.DATA_PATH, value)


_utf8_iso8859_l_table = dict((x, x.decode("iso-8859-1")) for x in map(chr, range(0, 256)))
def utf8_iso8859_1(data):
    return _utf8_iso8859_l_table.get(data.object[data.start]), data.start + 1

codecs.register_error("mixed-iso-8859-1", utf8_iso8859_1)


def decode_irc(x, redecode=True):
    try:
        if isinstance(x, unicode):
            if redecode:
                x = x.encode("iso-8859-1")
            else:
                return x
        return x.decode("utf-8", "mixed-iso-8859-1")
    except UnicodeDecodeError:
        return x


def strip_html(x):
    d = "".join(x.find_all(text=True))
    d = HTMLParser.HTMLParser().unescape(d)
    d = d.replace("\r", " ").replace("\n", " ")
    d = re.sub("\s{2,}", " ", d).strip()
    return d.encode("utf-8")


WHITESPACE_RE = re.compile("[ \n\t]+")
def tidy_whitespace(x):
    return WHITESPACE_RE.sub(" ", x)

