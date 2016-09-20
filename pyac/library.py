import json
import os
import urllib
try:
    from urllib2 import Request, urlopen
except ImportError:
    from urllib.request import Request, urlopen


class activeCollab(object):
    """ A python object with methods for interacting with activeCollab 3.x """

    def __init__(self, config_filename="~/.acrc", key=None,
                 url=None, user_id=None):
        if key is not None and url is not None and user_id is not None:
            self.key = key
            self.url = url
            self.user_id = user_id
        else:
            self.config_filename = config_filename
            self.config = self.load_config()
            self.key = self.config['key']
            self.url = self.config['url']
            self.user_id = self.config['user_id']
            if 'cache_location' in self.config:
                self.cache_location = self.config['cache_location']

    """ Make a call out to the activeCollab API. """
    def call_api(self, uri, params=None, cache=False):
        # @todo return results from cache
        url = self.url.rstrip("/") + "?auth_api_token=" + self.key + "&path_info=" \
            + uri + "&format=json"
        if params is not None:
            req = Request(url, urllib.urlencode(params))
        else:
            req = Request(url)
        res = urlopen(req)
        return json.loads(res.read())

    """ System Information. """

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

    """ This command will create a new company. If operation was successful,
        system will return details of the newly created company.
    """
    def add_company(self, name):
        params = {
            'status_update[name]': name,
            'submitted': 'submitted'
        }
        return self.call_api('people/add-company', params)

    """ Displays the properties of a specific company. """
    def get_company(self, company_id):
        return self.call_api('people/%s' % company_id)

    """ Shows details of a specific user account. """
    def get_user(self, company_id, user_id):
        return self.call_api('people/%s/users/%s' % (company_id, user_id))

    """ Display all, non-archived projects that this user has access to.
        In case of administrators and project managers, system will return
        all non-archived projects and properly populate is_member flag value
        (when 0, administrator and project manager can see and manage the
        project, but they are not
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
        return self.call_api('projects/%s' % project_id)

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

    """ Tasks
    Task fields:

        name (string) - Task name. A value for this field is required when
        a Task is created,
        body (text) - Full task description,
        visibility (integer) - Object visibility. 0 is private and 1 is normal
        visibility,
        category_id (integer) - Object category,
        label_id (integer) - Object label,
        milestone_id (integer) - ID of the parent milestone,
        priority (integer) - Priority can have one of five integer values,
        ranging from -2 (lowest) to 2 (highest). 0 is normal,
        assignee_id (integer) - User assigned to the Task,
        other_assignees (array) - People assigned to the Task,
        due_on (date) - Task due date,``
    """

    """ Get all tasks for the authenticated user.
    """
    def get_my_tasks(self):
        return self.call_api('/my-tasks')

    """ Lists all open and completed, non-archived tasks from a project.
        project_slug can be a project ID.
    """
    def get_project_tasks(self, project_slug):
        return self.call_api('/projects/%s/tasks' % project_slug)

    """ Displays all archived tasks from this project.
        project_slug can be a project ID.
    """
    def get_archived_project_tasks(self, project_slug):
        return self.call_api('/projects/%s/tasks/archive' % project_slug)

    """ Create a new task in the given project. """
    def add_task(self, project_slug, name, body=None):
        params = {
            'task[name]': name,
            'task[body]': body,
            'submitted': 'submitted'
        }
        return self.call_api('/projects/%s/tasks/add', params)

    """ Complete task in the project. """
    def complete_task(self, project_slug, task_id):
        params = {
            'submitted': 'submitted'
        }
        return self.call_api('/projects/%s/tasks/%s/complete' %
                             (project_slug, task_id), params)

    """ Displays details for a specific task. """
    def get_task(self, project_slug, task_id):
        return self.call_api('/projects/%s/tasks/%s' % (project_slug, task_id))

    """ discussions
        Discussion fields:

        name (string) - Discussion topic. This field is required when topic
        is created,
        body (string) - First message body (required),
        category_id (integer) - Discussion category id,
        visibility (integer) - Discussion visibility. 0 is private and 1 is
        normal visibility,
        milestone_id (integer) - ID of parent milestone.
    """

    """ Displays all non-archived discussions in a project. """
    def get_discussions(self, project_slug):
        return self.call_api('/projects/%s/discussions')

    """ Display discussion details. """
    def get_discussion(self, project_slug, discussion_id):
        return self.call_api('/projects/%s/discussions/%s' %
                             (project_slug, discussion_id))

    """ Time & Expenses """
    def get_times_and_expenses_by_project(self, project_id, limit=0):
        """ This command will display last 300 time records and expenses in a
            given project. If you wish to return all time records and expenses
            from a project, set limit to 1.
        """
        return self.call_api('projects/%s/tracking&dont_limit_result=%s' %
                             (project_id, limit))

    def add_time_to_project(self, project_id, value, user_id, record_date,
                            job_type_id):
        """ Adds a new time record to the time log in a defined project. """
        params = {
            'time_record[value]': value,
            'time_record[user_id]': user_id,
            'time_record[record_date]': record_date,
            'time_record[job_type_id]': job_type_id,
            'submitted': 'submitted',
        }
        return self.call_api('projects/%s/tracking/time/add' %
                             project_id, params)

    def add_time_to_task(self, project_id, task_id, value, user_id,
                         record_date, job_type_id, billable_status, summary):
        """ Adds a new time record to the time log in a defined project
            task.
        """
        params = {
            'time_record[value]': value,
            'time_record[user_id]': user_id,
            'time_record[record_date]': record_date,
            'time_record[job_type_id]': job_type_id,
            'time_record[billable_status]': billable_status,
            'time_record[summary]': summary,
            'submitted': 'submitted',
        }
        return self.call_api('projects/%s/tasks/%s/tracking/time/add' %
                             (project_id, task_id), params)

    def get_time_record(self, project_id, record_id):
        """ Displays time record details. """
        return self.call_api('projects/%s/tracking/time/%s' %
                             (project_id, record_id))

    """ Lists the 50 most recent status messages. """
    def get_status_messages(self):
        return self.call_api('status')

    """ This command will submit a new status message.
        Example request:
            status_update[message]=New status message
            submitted=submitted
    """
    def add_status_message(self, message):
        params = {
            'status_update[message]': message,
            'submitted': 'submitted'
        }
        return self.call_api('status/add', params)

    """ Subtasks
        List of available subtask fields:

        body (text) - The subtasktask name. A value for this field is required
        when a new task is added;
        assignee (integer) - Person assigned to the object.
        priority (integer) - Priority can have five integer values ranging from
        -2 (lowest) to 2 (highest). 0 is normal;
        label_id (date) - Label id of the subtask;
        due_on (date) - When the subtask is due;
    """

    """ Displays all subtasks for a given project object in a specific
        project.
    """
    def get_subtasks(self, project_slug):
        return self.call_api('/projects/%s/subtasks' % project_slug)

    """ Displays subtask details. """
    def get_subtask(self, project_slug, subtask_id):
        return self.call_api('/projects/%s/subtasks/%s' %
                             (project_slug, subtask_id))

    """ Comments """
    def add_comment(self, context, message):
        params = {
            'comment[body]': message,
            'submitted': 'submitted'
        }
        return self.call_api('%s/comments/add' % context, params)

    """ Add comment to task. """
    def add_comment_to_task(self, project_slug, task_id, message):
        context = '/projects/%s/tasks/%s' % (project_slug, task_id)
        return self.add_comment(context, message)

    def get_comments(self, project_slug, task_id):
        return self.call_api('/projects/%s/tasks/%s/comments' %
                             (project_slug, task_id))

    """ Helpers """

    def load_config(self):
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
