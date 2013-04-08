import commands
import http
import re
import config
import json
import urlparse
import github3
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

    tokens = args.split()
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

    if gh.repository(owner, repo) is None:
        return "Could not find repository {owner}/{repo}".format(owner=owner, repo=repo)

    if subcommand == 'search':
        return _ticket_search(callback, owner, repo, subargs)
    elif subcommand == 'show':
        return _ticket_show(callback, owner, repo, subargs)
    elif subcommand == 'create':
        return _ticket_create(callback, owner, repo, subargs)
    else:
        return "Unrecognised !ticket subcommand: %s" % subcommand

def _format_issue(issue):
    return "#{number} {title} ({state}) - {url}".format(number=issue.number, title=issue.title, state=issue.state, url=issue.html_url)

def _ticket_search(callback, owner, repo, args):
    """
    Search for issues; note just open issues for now...
    """

    output = []
    def s(issue_type=None):
        if issue_type is None:
            open_issues = s('open')
            closed_issues = s('closed')
            return sorted(open_issues + closed_issues, key=lambda issue: issue.number)
        return gh.search_issues(owner, repo, issue_type, ' '.join(args))

    issues = s()
    if not issues:
        return "No issues found on {owner}/{repo} matching '{term}'".format(owner=owner, repo=repo, term=' '.join(args))
    for issue in issues:
        output.append(_format_issue(issue))

    return '\n'.join(output)


def _ticket_show(callback, owner, repo, args):
    output = []

    for arg in args:
        try:
            issue_number = int(arg)
        except ValueError:
            output.append("Not a valid issue number: '%s'" % arg)
            continue
        issue = gh.issue(owner, repo, issue_number)
        if issue is None:
            output.append("No issue found in {owner}/{repo} with number {issue_number}".format(owner=owner, repo=repo, issue_number=issue_number))
            continue
        output.append(_format_issue(issue))

    return '\n'.join(output)


def _ticket_create(callback, owner, repo, args):
    assignee = None

    if args[0][0] == '@': # We have an assignee!
        username = args[0][1:]
        r = gh.repository(owner, repo) #Ok, maybe "repo" was a poor parameter name
        if not r.is_assignee(username): # TODO Consider patch to library for better name?
            return "@{username} isn't a valid assignee for issues on {owner}/{repo}".format(username=username, owner=owner, repo=repo)
        assignee = username
        args = args[1:]

    issue_title = ' '.join(args)
    issue = gh.create_issue(owner, repo, issue_title, assignee=assignee)

    return "Created %s" % _format_issue(issue)

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

if __name__ == '__main__':
    print("Generating a GitHub auth token")
    username = raw_input("Username: ")
    password = raw_input("Password: ")
    note_url = "https://bitbucket.org/chrisporter/holly/"
    authorization = github3.GitHub().authorize(username, password, ['repo'], note_url=note_url)
    print authorization.to_json()
