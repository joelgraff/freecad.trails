# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2018 Joel Graff <monograff76@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
Publisher base class
"""

from ..support.const import Const

class PublisherEvents(Const):
    """
    Events for Publisher class
    """

    ALL_EVENTS = 0
    TASK_EVENT = 1
    NODE_EVENT = 2
    WIRE_EVENT = 4
    CURVE_EVENT = 8
    ALIGNMENT_EVENT = 16

class Publisher:
    """
    Base class for publisher classes
    """

    def __init__(self, pubid):
        """
        Constructor
        """

        super().__init__(pubid)

        self.id = "Publisher " + pubid

        event_count = len(PublisherEvents.__dict__.keys()) - 4

        self.event_max = (2**(event_count - 1)) - 1
        self.event_indices = [(2**_x) for _x in range(0, event_count + 1)]
        self.events = {event: {} for event in self.event_indices}

    def get_subscribers(self, events=0):
        """
        Return subscribers registered for selected event
        """

        _result = []

        if not events:
            events = self.event_max

        for _i in self.event_indices:

            if events & _i:
                _result.append(self.events[_i])

        return _result

    def register(self, who, events, callback=None):
        """
        Callback registration for subscribers
        """
        if not callback:
            callback = getattr(who, 'notify')

        _list = self.get_subscribers(events)

        for _e in _list:
            if not who in _e:
                _e[who] = callback

    def unregister(self, who, events):
        """
        Callback unregistration for subscribers
        """

        _list = self.get_subscribers(events)

        for _e in _list:
            if who in _e:
                del _e[who]

    def dispatch(self, event, message):
        """
        Message dispatch
        """

        _list = self.get_subscribers(event)

        for _e in _list:
            for _c in _e.values():
                _c(event, message)
