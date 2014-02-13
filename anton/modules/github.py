import json
import re
import urlparse
from anton import http, config


@http.register(re.compile("^/github/post-receive$"))
def http_handler(env, m, irc):
    try:
        content_length = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        content_length = 0

    body = env['wsgi.input'].read(content_length)
    data = urlparse.parse_qs(body)

    payload = json.loads(data['payload'][0])
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
        irc.chanmsg(config.GITHUB_CHANNEL, output)
    return "application/json", json.dumps(payload)
