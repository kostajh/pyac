import json
import os
import time
import datetime
import urllib2

class activeCollab(object):
    """ A python object with methods for interacting with activeCollab 3.x """

    def __init__(self, config_filename="~/.acrc"):
        self.config_filename = config_filename
        self.config = self._load_config()
        self.key = self.config['key']
        self.url = self.config['url']
        self.user_id = self.config['user_id']

    def call_api(self, uri, cache=False):
        # @todo return results from cache
        url = self.url.rstrip("/") + "?auth_api_token=" + self.key + "&path_info=" + uri + "&format=json"
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        return json.loads(res.read())

    """ GET requests """

    """ System Information.
        @see https://www.activecollab.com/docs/manuals/developers-version-3/api/system-information
    """

    """ Returns system information about the installation you are working with.
        This information includes system versions; info about logged in users;
        the mode the API is in etc.
    """
    def get_info(self):
        return self.call_api('info')

    """ Lists all available project labels. """
    def get_project_labels(self):
        return self.call_api('info/labels/project')

    """ Lists all available assignment labels. These labels are used by tasks
        and subtasks.
    """
    def get_assignment_labels(self):
        return self.call_api('info/labels/assignment')

    """ Lists all system roles and role details (permissions included). """
    def get_roles(self):
        return self.call_api('info/roles')

    """ Lists all project roles and displays their permissions. """
    def get_project_roles(self):
        return self.call_api('info/roles/project')

    """ Lists all active companies that are defined in People section. """
    def get_people(self):
        return self.call_api('people')

    """ Displays the properties of a specific company. """
    def get_company(self, company_id):
        return self.call_api('people/%d' % company_id)

    """ Shows details of a specific user account. """
    def get_user(self, company_id, user_id):
        return self.call_api('people/%d/users/%d' % (company_id, user_id))

    """ Display all, non-archived projects that this user has access to. In case
        of administrators and project managers, system will return all non-archived
        projects and properly populate is_member flag value (when 0, administrator
        and project manager can see and manage the project, but they are not
        directly involved with it).
    """
    def get_projects(self):
        return self.call_api('projects')

    """ Display all archived projects that this user has access to. In case of
        administrators and project managers, system will return all archived
        projects and properly populate is_member flag value (when 0,
        administrator and project manager can see and manage the project, but
        they are not directly involved with it).
    """
    def get_archived_projects(self):
        return self.call_api('projects/archive')

    """ Shows properties of the specific project. """
    def get_project(self, project_id):
        return self.call_api('projects/%d' % project_id)

    """ Displays the list of people involved with the project and the
        permissions included in their Project Role. Project Permissions are
        organized per module and have four possible values:

        0 - no access;
        1 - has access, but can't create or manage objects;
        2 - has access and permission to create objects in a given module;
        3 - has access, creation and management permissions in a given module.
    """
    def get_project_people(self, project_slug):
        return self.call_api('projects/%s/people' % project_slug)

    """ @todo
        - tasks
        - milestones
        - discussions
        - time and expenses
        - status message
        - Contexts
            - categories
            - subtasks
            - comments
            - attachments
            - completion status
            - reminders
    """

    """ POST requests """

    """ Helpers """

    def _load_config(self):
        """ Load ~/.acrc into a python dict

        >>> ac = activeCollab()
        >>> config = ac.load_config()
        >>> config['key']
        'SOME_SECRET_KEY'

        """

        with open(os.path.expanduser(self.config_filename), 'r') as f:
            lines = f.readlines()

        _usable = lambda l: not(l.startswith('#') or l.strip() == '')
        lines = filter(_usable, lines)

        def _build_config(key, value, d):
            """ Called recursively to split up keys """
            pieces = key.split('.', 1)
            if len(pieces) == 1:
                d[pieces[0]] = value.strip()
            else:
                d[pieces[0]] = _build_config(pieces[1], value, {})

            return d

        d = {}
        for line in lines:
            if '=' not in line:
                continue

            key, value = line.split('=')
            d = _build_config(key, value, d)

        return d
