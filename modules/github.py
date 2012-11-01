import commands
import http
import re
import config
import json

try:
    GITHUB_CHANNEL = config.GITHUB_CHANNEL
except AttributeError:
    GITHUB_CHANNEL = "#twilightzone"

@http.register(re.compile("^/github/post-receive$"))
def http_handler(env, m, irc):
    payload = json.loads(env['wsgi.input'].read())
    repository = payload['repository']

    for commit in payload['commits']:
        message = commit['message']
        message = re.sub(r'\n.*', r'', message)

        output = '{author} pushed a commit to {owner}/{repo_name} ({commit_url}): "{message}"'.format(
            author=commit['author']['name'],
            owner=repository['owner']['name'],
            repo_name=repository['name'],
            commit_url=commit['url'],
            message=message,
        )
        irc.chanmsg(GITHUB_CHANNEL, output)
    return "application/json", json.dumps(payload)
