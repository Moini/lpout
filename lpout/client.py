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
Access to the launchpad client, singleton only.
"""

import os

from lpout import __pkgname__
from launchpadlib import launchpad

CACHE_DIR = os.path.abspath(os.path.expanduser('~/.cache/launchpadlib'))
CONNECTION = None

class Client(object):
    """Connect to the launchpad client and provide access to projects"""

    @property
    def connection(self):
        global CONNECTION
        if CONNECTION is None:
            if not os.path.isdir(CACHE_DIR):
                os.makedirs(CACHE_DIR)
            CONNECTION = launchpad.Launchpad.login_anonymously(
                 __pkgname__, 'production', CACHE_DIR, version='devel')
        return CONNECTION

    def project(self, name):
        """Return wrapped project object"""
        from lpout.objects import Project
        return Project(self.connection.projects[name], name=name)

    @classmethod
    def connect(self, **kw):
        from lpout import objects
        for name, fn in kw.items():
            getattr(objects, name).connect(fn)

