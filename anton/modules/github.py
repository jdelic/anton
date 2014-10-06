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

    lines = output_lines(payload)

    for line in lines:
        irc.chanmsg(config.GITHUB_CHANNEL, line)

    return "application/json", json.dumps(payload)


def output_lines(payload):
    lines = []

    pusher = payload['pusher']['name']
    ref = payload['ref']
    repo = payload['repository']['full_name']

    if (payload['head_commit']):
        commits = len(payload['commits'])
        output = u'{pusher} pushed {commits} commit(s) to {ref} on {repo} ({compare_url}): "{message}"'.format(
            pusher=pusher,
            commits=commits,
            ref=ref,
            repo=repo,
            compare_url=payload['compare'],
            message=payload['head_commit']['message'],
        ).encode('utf-8')
        lines.append(output)

    if payload['forced']:
        alert = u'ALERT ALERT ALERT {pusher} **FORCE PUSHED** TO {ref} ON {repo}'.format(
            pusher=pusher,
            ref=ref,
            repo = repo,
        ).encode('utf-8')
        lines.append(alert)

    return lines

if __name__ == '__main__':
    import sys

    with open(sys.argv[1]) as json_file:
        data = json.load(json_file)

    for line in output_lines(data):
        print line
