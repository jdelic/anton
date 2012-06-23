import commands
import urllib
import util

from BeautifulSoup import BeautifulSoup as soup

class NotDefinedException(Exception):
  pass

@commands.register("!slogan")
def slogan(callback, term):
  url = "http://thesurrealist.co.uk/slogan.cgi?word=%s" % urllib.quote(term)

  f = urllib.urlopen(url)
  try:
    data = f.read()
  finally:
    f.close()

  v = parse_html(data)
  if v is not None:
    return v

def parse_html(data):
  page = soup(data)

  t = page.find("a", {"class": "h1a"})
  return util.strip_html(t)

if __name__ == "__main__":
  print slogan(None, "!slogan wibble")
