import urllib
from anton import util
from bs4 import BeautifulSoup
import urlparse
from anton import commands


class AppURLopener(urllib.FancyURLopener):
    version = "Links"


class NoResultsException(Exception):
    pass


@commands.register(["!g", "!google"])
def google(callback, query):
    url = "http://www.google.com/search?q=%s&ie=UTF-8" % urllib.quote(query.encode("utf8"))

    f = AppURLopener().open(url)
    try:
        data = f.read()
    finally:
        f.close()

    try:
        results = parse_data(data)
        if not results:
            raise NoResultsException
    except NoResultsException:
        return "no results ;("

    result = results[0]

    if result["type"] == "result":
        return "%s (%s)" % (result["href"], result["text"])
    elif result["type"] == "string":
        return result["string"]


def parse_data(data):
    page = BeautifulSoup(data)

    results = page.find("div", id="res")
    if results is None:
        raise NoResultsException

    calc = results.find("img", src="/images/icons/onebox/calculator-40.gif")
    if calc is not None:
        calc = results.find("h2", {"class": "r"})
        if calc is not None:
            superscripts = calc.find_all("sup")
            if superscripts is not None and len(superscripts):
                for x in superscripts:
                    x.contents[0].replaceWith("^" + x.contents[0])
            return [dict(type="string", string=util.strip_html(calc).decode("utf-8"))]

    nresults = results.find_all("li", {"class": "g"})
    if len(nresults) == 0:
        raise NoResultsException

    processed_results = []
    for x in nresults:
        a_tag = x.find("a")
        if a_tag is not None:
            processed_results.append(
                dict(type="result", href=urlparse.parse_qs(urlparse.urlparse(a_tag["href"]).query)["q"][0],
                     text=util.strip_html(a_tag).decode("utf-8")))

    return processed_results
