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
Format objects for output, usually into dictionaries.
"""

from .base import *

from collections import OrderedDict

LABELS = OrderedDict([
    # LP-NAME, COLOR, IS_OPEN, GITLAB-NAME (if unset, no label is created)
    ('UNKNOWN',    ('#ffdabe', True, None)),
    ('NEW',        ('#ffdabe', True, None)),
    ('INCOMPLETE', ('#ffdabe', True, 'Incomplete')),
    ('CONFIRMED',  ('#f4f1a4', True, 'Confirmed')),
    ('TRIAGED',    ('#f4f1a4', True, 'Triaged')),
    ('IN PROGRESS',   ('#cbe7ef', True, 'In Progress')),
    ('FIX COMMITTED', ('#cbe7ef', False, 'Fix Committed')),
    ('FIX RELEASED',  ('#cef1a0', False, None)),
    ('EXPIRED',    ('#dddddd', False, None)),
    ("WON'T FIX",  ('#dddddd', False, 'Will Not Fix')),
    ('OPINION',    ('#dddddd', False, False)),
    ('INVALID',    ('#dddddd', False, False)),

    # LP-NAME, COLOR, PRIORITY, GITLAB-NAME
    ('UNDECIDED',  ('#666666', None, None)),
    ('WISHLIST',   ('#724dc8', 2, 'Wishlist')),
    ('LOW',        ('#38b44a', 4, 'Low')),
    ('MEDIUM',     ('#19b6ee', 6, 'Medium')),
    ('HIGH',       ('#efb73e', 8, 'High')),
    ('CRITICAL',   ('#df382c', 10, 'Critical')),
])
STATUS = [name for name, (c, o, l) in LABELS.items() if o is False],\
         [name for name, (c, o, l) in LABELS.items() if o is True]

