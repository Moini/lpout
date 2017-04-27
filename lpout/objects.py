#
# Copyright (C) 2017 - Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Solid API objects for launchpad.
"""

import base64

from lpout.base import IterObject, IterObjects, ApiObj
from lpout.constants import STATUS, LABELS

class Bug(ApiObj):
    @classmethod
    def get_name(self, link):
        parts = link.split('/')
        return "%s/%d" % (parts[-3], int(parts[-1]))

    @classmethod
    def get_link(self, name):
        return 'https://api.launchpad.net/devel/%s/+bug/%s' % name.split('/', 1)

    @IterObject(dict)
    def data(self):
        task = self.connection()
	bug = task.bug
	for key in ('status', 'importance',):
            label = Label(name=getattr(task, key))
	    yield (key, label)
            if label.data()['is_open'] in (True, False):
                yield ('is_open', label.data()['is_open'])

	for key in ('id', 'title', 'description', 'tags', 'security_related', 'web_link'):
	    yield (key, getattr(bug, key))

	for key in ('date_created', 'date_assigned', 'date_closed', 'date_fix_committed', 'date_fix_released'):
	    if getattr(task, key):
		yield (key, getattr(task, key))

	yield ('assignee', User(link=task.assignee_link))
	yield ('owner', User(link=task.owner_link))
	yield ('milestone', Milestone(link=task.milestone_link))
	yield ('duplicate_of', self.get_task(bug.duplicate_of_link))

	# Don't query the message collection if there are none
	if bug.message_count > 1:
            attachments = [Attachment(att).inline() for att in bug.attachments]
            yield ('comments', [Comment(msg, attachments=attachments).inline()
                    for msg in list(bug.messages)[1:]])

    def get_task(self, name):
        """Because bug and tasks aren't the same, we have to request a bug link"""
        # We go through ALL this because we don't want to make a premature
        # http call to launchpad which is known for being slow.
        if name is not None:
            # prepend the project to the bug_id as the new name
            project = repr(self).rsplit('/', 1)[0]
            bug_id = str(name).split('/')[-1]
            return Bug(link='/'.join([project, bug_id]))
        return None


class Milestone(ApiObj):
    @classmethod
    def get_name(self, link):
        return link.rsplit('/', 1)[-1]


class User(ApiObj):
    @classmethod
    def get_name(self, link):
        return link.rsplit('~', 1)[-1]


class Comment(ApiObj):
    def __init__(self, *args, **kw):
        self.atts = kw.pop('attachments', [])
        super(Comment, self).__init__(*args, **kw)

    @classmethod
    def get_name(self, link):
        parts = link.split('/')
        return "%d/%d" % (int(parts[-3]), int(parts[-1]))

    @IterObject(dict)
    def data(self):
        message = self.connection()
	yield ('owner', User(link=message.owner_link))
	yield ('date_created', message.date_created)
        yield ('bug_id', repr(self).split('/')[0])
	yield ('id', repr(self))
	if message.content:
	    yield ('content', message.content)
        for att in self.atts:
            if str(att['message']) == str(self):
                yield ('attachment', att)


class Attachment(ApiObj):
    @classmethod
    def get_name(self, link):
        return link.split('+attachment/', 1)[-1]

    def __getitem__(self, name):
        if name == 'message':
            return Comment(self.connection().message)

    @IterObject(dict)
    def data(self):
        at = self.connection()
        fh = at.data.open()
        yield('id', repr(self))
        yield('message', Comment(at.message))
        yield('data', base64.b64encode(fh.read()))
        yield('content-type', fh.content_type)
        yield('filename', fh.filename)
        yield('title', at.title)


class Label(ApiObj):
    """A label is any status or tag that in Git based systems is accounted as just a 'label'"""
    def get_link(self, name):
        return name # There is no URL/link for labels

    def data(self):
        label = LABELS.get(repr(self).upper(), ('#fff', None, repr(self)))
        data = dict(zip(('color', 'priority', 'name'), label))
        if data['priority'] in (True, False):
            data['is_open'] = data['priority']
            data['priority'] = None
        else:
            data['is_open'] = None
        return data


class Project(ApiObj):
    def get_tags(self):
        return self.connection().official_bug_tags

    @IterObjects(Bug)
    def get_bugs(self, is_open=None, **kwargs):
        if is_open is not None:
            kwargs['status'] = STATUS[is_open]
        return self.connection().searchTasks(**kwargs)

    @IterObjects(Milestone)
    def get_milestones(self, is_open=None):
        if is_open is True:
            return self.connection().active_milestones
        return self.connection().all_milestones

