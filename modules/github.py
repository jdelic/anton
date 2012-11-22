import commands
import http
import re
import config
import json
import urlparse
import github3
import shlex
import logging

try:
    GITHUB_CHANNEL = config.GITHUB_CHANNEL
except AttributeError:
    GITHUB_CHANNEL = "#twilightzone"

GITHUB_AUTH_TOKEN = None
GITHUB_DEFAULT_ORGANIZATION = None
GITHUB_DEFAULT_REPO = None

try:
    GITHUB_AUTH_TOKEN = config.GITHUB_AUTH_TOKEN
    gh = github3.login(token=GITHUB_AUTH_TOKEN)

    GITHUB_DEFAULT_ORGANIZATION = config.GITHUB_DEFAULT_ORGANIZATION
    GITHUB_DEFAULT_REPO = config.GITHUB_DEFAULT_REPO
except AttributeError:
    pass

@commands.register("!ticket")
def ticket(callback, args):
    if GITHUB_AUTH_TOKEN is None:
        return "No value for config.GITHUB_AUTH_TOKEN, no !ticket for you :("

    tokens = shlex.split(args)
    if len(tokens) < 2:
        return "Not enough arguments"
    subcommand = tokens[0]
    subargs = tokens[1:]

    # if first args token looks like a repo - "owner/repo" then use that, else fallback to GITHUB_DEFAULT_ORGANIZATION/GITHUB_DEFAULT_REPO
    if '/' in subargs[0]:
        owner,repo = subargs[0].split('/')
        subargs = subargs[1:]
    else:
        owner,repo = GITHUB_DEFAULT_ORGANIZATION, GITHUB_DEFAULT_REPO

    if subcommand == 'search':
        return _ticket_search(callback, owner, repo, subargs)
    else:
        return "Unrecognised !ticket subcommand: %s" % subcommand

def _format_issue(issue):
    return "#{number} {title} ({state}) - {url}".format(number=issue.number, title=issue.title, state=issue.state, url=issue.html_url)

def _ticket_search(callback, owner, repo, args):
    """
    Search for issues; note just open issues for now...
    """

    output = []
    issues = gh.search_issues(owner, repo, 'open', ' '.join(args))
    if not issues:
        return "No issues found on {owner}/{repo} matching '{term}'".format(owner=owner, repo=repo, term=' '.join(args))
    for issue in issues:
        output.append(_format_issue(issue))

    return '\n'.join(output)


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
        irc.chanmsg(GITHUB_CHANNEL, output)
    return "application/json", json.dumps(payload)
