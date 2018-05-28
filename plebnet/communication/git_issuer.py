import json
import requests

from plebnet.utilities import logger
from plebnet.settings import plebnet_settings


def make_github_issue(title, body=None, labels=None):
    settings = plebnet_settings.get_instance()
    if not settings.github_active(): return

    username = settings.github_username()
    password = settings.github_password()
    repo_owner = settings.github_owner()
    repo_name = settings.github_repo()

    """Create an issue on github.com using the given parameters."""
    # Our url to create issues via POST
    url = 'https://api.github.com/repos/%s/%s/issues' % (repo_owner, repo_name)
    # Create an authenticated session to create the issue
    session = requests.Session()
    session.auth = (username, password)
    # Create our issue
    issue = {'title': title,
             'body': body,
             'labels': labels}
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        logger.log('Successfully created Issue "%s"' % title)
    else:
        logger.warning('Could not create Issue "%s"' % title)
        logger.log('Response:', r.content)
