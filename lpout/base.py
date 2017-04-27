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
Generic, non-API related functions.
"""

import inspect
from collections import defaultdict

def IterObject(t=list):
    """Decorator: Create an object from a generator function, default is list"""
    def _outer(f):
        def _inner(*args, **kwargs):
            return t(f(*args, **kwargs))
        return _inner
    return _outer


def IterObjects(t=str):
    """Decorator: Pass each item from a generator through a call, default is str"""
    def _outer(f):
        def _inner(*args, **kwargs):
            for item in f(*args, **kwargs):
                yield t(item)
        return _inner
    return _outer


def WebLink(f):
    """ 
    A web link means that the id we're interested in is within the web_link
    url. So we don't need to download the whole object to return the value.
    """
    def _inner(obj):
        if obj is None:
            return None
        elif not isinstance(obj, basestring):
            obj = obj.web_link
        return f(obj)
    return _inner


class ApiObj(object):
    """API Base Object"""
    signal = None
    already = defaultdict(set)

    def __new__(cls, conn=None, **kw):
        kw['conn'] = conn
        # If all inputs are None, then this is a None object
        if all([kw.get(n, None) is None for n in ('name', 'link', 'conn')]):
            return None
        return super(ApiObj, cls).__new__(cls, **kw)

    def __init__(self, conn=None, name=None, link=None, **kw):
        # Name is critical for not repeating the same import
        if name is None:
            if link is not None:
                name = self.get_name(link)
            elif conn is not None:
                name = self.get_name(conn.self_link)
            else:
                raise KeyError("Can not create %s with no unique name!" % self.cls())

        if not hasattr(self, '_conn'):
            self.kwargs = kw
            self._conn = conn
            self._name = name
            self._link = link

            if self.signal and name not in self.already[self.cls()]:
                self.already[self.cls()].add(name)
                kw = kw.copy()
                kw['name'] = name
                if 'data' in self.signal_args:
                    # Do the data call ONLY if data is requested.
                    kw['data'] = self.data()
                for arg in kw:
                    if arg not in self.signal_args:
                        kw.pop(arg)
                self.iid = self.signal(**kw)

    def __str__(self):
        """Always returns the link of the object"""
        if self._link is None:
            if self._conn:
                self._link = self._conn.self_link
            else:
                self._link = self.get_link(self._name)
        return self._link

    def __repr__(self):
        """Always returns the useful target name of the object"""
        return getattr(self, 'iid', None) or self._name

    @classmethod
    def cls(cls):
        return cls.__name__

    def connection(self):
        """Always returns the linked connection if available"""
        if self._conn is None:
            from .client import Client
            self._conn = Client().connection.load(str(self))
        return self._conn

    @classmethod
    def connect(cls, signal):
        """Connect up a signal for this type of object, submits the data for each iter"""
        cls.signal_args = inspect.getargspec(signal).args[1:]
        cls.signal = signal

    @classmethod
    def disconnect(cls):
        """Remove any connected signal when importing"""
        cls.signal = None

    def get_dict(self):
        """Return a dictionary containing all objects for this"""
        return dict(self.data())

    @classmethod
    def get_name(cls, link):
        """Formats an API link into a usable name/id"""
        raise NotImplementedError("No %s.get_name(link) method" % cls.cls())

    @classmethod
    def get_link(cls, name):
        """Formats a name into a usable API link"""
        raise NotImplementedError("No %s.get_link(name) method" % cls.cls())

    @IterObject(dict)
    def data(self):
        """Implemented in child process to produce creation/update dict"""
        conn = self.connection()
        for key in conn.lp_attributes:
            if key not in ('http_etag', 'self_link'):
                yield (key, getattr(conn, key))

    def inline(self):
        """A split in the logic between elements with signals and those without
        
        If an object class has a signal, then we return the self (object as link)

        If the object class does not have a signal, then we can inline the object's data
        
        """
        if self.signal:
            return self
        else:
            return self.data()

