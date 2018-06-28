"""
This file contains methods for communication via Github. It can be used to send
files (via gist) or to create issues.

NOTE: This file should contain restricted dependencies with other classes, as
these make the communication more error prone, while these methods are used for
error handling.

"""
import requests
import sys
import traceback
import json

from plebnet.utilities import logger
from plebnet.settings import plebnet_settings


def handle_error(title, trace_back=' ', labels=['bug']):
    """
    This method can be called with information regarding an error. It creates a git issue about it and
    send the log files along.
    :param title: The title of the error
    :type title: String
    :param trace_back: The trace back resulting in the error
    :type trace_back: String
    :param labels: the labels to attach to the issue
    """
    # Only execute if PlebNet is activated
    settings = plebnet_settings.get_instance()
    if not settings.github_active(): return

    body = \
        "An error occurred at a plebbot agent\n\r" \
        "\n\r" \
        "The plebnet nick is _%s_ \r\n"\
        "More info can be added here later on\n\r" \
        "\n\r" \
        "\n\r" \
        "The track back of the error:\n\r" \
        "\n\r" \
        "```\n\r" \
        "%s\n\r" \
        "```\n\r" \
        "\n\r" \
        "The log file can be found [here](%s)\n\r" \
        "\n\r" \
        "More details regarding this post can be found [here](%s)\n\r" \
        "\n\r" \
        "\n\r" \
        "Good luck fixing this!"

    full_link, gist_link = create_gist()
    body = body % (settings.irc_nick(), trace_back, gist_link, full_link)
    create_issue(title, body, labels)


def create_issue(title, body, labels):
    """
    This method creates a github issue when called.
    :param title: The title of the issue
    :type title: String
    :param body: The body text of the issue
    :type body: String
    :param labels: The labels which should be attached to the issue
    :type labels: String[]
    """
    # Only execute if PlebNet is activated
    settings = plebnet_settings.get_instance()
    if not settings.github_active(): return

    try:
        # Collect variables
        username = settings.github_username()
        password = settings.github_password()
        repo_owner = settings.github_owner()
        repo_name = settings.github_repo()

        # Our url to create issues via POST
        url = 'https://api.github.com/repos/%s/%s/issues' % (repo_owner, repo_name)

        # Create an authenticated session to create the issue
        session = requests.Session()
        session.auth = (username, password)

        # Create our issue
        issue = {'title': title, 'body': body, 'labels': labels}

        # Add the issue to our repository
        r = session.post(url, json.dumps(issue))

        # Inform about the results
        if r.status_code == 201:
            logger.success('Successfully created Issue "%s"' % title)
        else:
            logger.warning('Could not create Issue "%s"' % title)
            logger.log(r.content, 'Response:')
    except:
        logger.error(sys.exc_info()[0], "git_issuer send")
        logger.error(traceback.format_exc())


def create_gist(filename=None):
    """
    This method can be used to send a file to github via gist.
    :param filename: the file to send, if left empty, the log file is send
    :type filename: String
    """
    # Only execute if PlebNet is activated
    settings = plebnet_settings.get_instance()
    if not settings.github_active():
        return
    if not filename:
        filename = settings.logger_file()

    try:
        # Collect variables
        username = settings.github_username()
        password = settings.github_password()
        bot_name = settings.irc_nick()

        # Get the log files
        content = open(filename, 'r').read()

        # Our url to create issues via POST
        url = 'https://api.github.com/gists'

        # Create an authenticated session to create the issue
        session = requests.Session()
        session.auth = (username, password)

        # Create our issue
        gist = {
            "description": "The logfile for %s" % bot_name,
            "public": True,
            "files": {
                "logfile.txt": {
                    "content": content
                }
            }
        }
        r = session.post(url, json.dumps(gist))

        # Inform about the results
        if r.status_code == 201:
            logger.success('Successfully created gist')
        else:
            logger.warning('Could not create gist')
            logger.log(r.content, 'Response:')
        return r.json()['url'], r.json()['html_url']

    except:
        logger.error(sys.exc_info()[0], "git_issuer gist")
        logger.error(traceback.format_exc())
        return None, None
