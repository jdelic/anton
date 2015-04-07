"""
HTTP endpoint for the Jenkins Notification Plugin
(https://wiki.jenkins-ci.org/display/JENKINS/Notification+Plugin) to POST JSON to.

Note you may want the Jenkins IRC Plugin (https://wiki.jenkins-ci.org/display/JENKINS/IRC+Plugin);
this was written to avoid bot proliferation, and also to add a few features more easily (colour
and start notification)

Also note that the Notification Plugin docs at the above link (at time of writing) are incorrect
regarding the JSON data POSTed; the code here (at time of writing) uses what the actual current
plugin version sends...
"""
import logging

from anton import http
import re
from anton import config
import json

try:
    JENKINS_CHANNEL = config.JENKINS_CHANNEL
except AttributeError:
    JENKINS_CHANNEL = "#twilightzone"


_log = logging.getLogger(__name__)


@http.register(re.compile("^/jenkins$"))
def http_handler(env, m, irc):
    try:
        input = env['wsgi.input'].read()
        payload = json.loads(input)
    except ValueError as e:
        _log.error("Can't decode input: %s", input, exc_info=True)
        return

    build = payload['build']
    if build['phase'] != 'FINISHED' and build['phase'] != 'FINALIZED':  # No need for STARTED/COMPLETED/other
        return

    status = build['status']

    # Shonk, for colour
    if status == "FAILURE":
        status = "\00305%s\03" % status
    if status == "SUCCESS":
        status = "\00309%s\03" % status

    output = "Project {project_name} build #{build_number}: {status} - {url}".format(
        project_name=payload['name'],
        build_number=build['number'],
        status=status,
        url=build['full_url'],
    )
    irc.chanmsg(JENKINS_CHANNEL, output)
    return "text/plain", output
