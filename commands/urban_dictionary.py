import commands
import urllib
import util

from BeautifulSoup import BeautifulSoup as soup

class NotDefinedException(Exception):
  pass

@commands.register("!ud")
def urban_dictionary(callback, term):
  url = "http://www.urbandictionary.com/define.php?term=%s" % urllib.quote(term.encode("utf8"))

  f = urllib.urlopen(url)
  try:
    data = f.read()
  finally:
    f.close()

  try:
    entries = parse_html(data)
    if not entries:
      raise NotDefinedException
  except NotDefinedException:
    return "not defined :("

  result = entries[0]

  return [
    "%s: %s" % (result["word"], result["definition"]),
    "e.g. %s" % result["example"]
  ]

def parse_html(data):
  page = soup(data)

  if page.find("div", id="not_defined_yet"):
    raise NotDefinedException

  trs = page.find("table", id="entries").findAll("tr", recursive=False)

  entries = []
  for x in trs:
    td = x.find("td", {"class": "word"})
    if td:
      word = td
    else:
      td = x.find("td", {"class": "text"})
      if td:
        if td.get("id") == "image_set":
          continue
        entries.append(
          dict(word=word,
               definition=td.find("div", {"class": "definition"}),
               example=td.find("div", {"class": "example"})
              ))

  entries = [dict((key, util.strip_html(value)) for key, value in x.items()) for x in entries]
  return entries

