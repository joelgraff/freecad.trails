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

class _EVT(Const):

    MSB = 6
    LSB = 2**MSB

    @staticmethod
    def get(base, num):
        """Calc the base-2 flag value"""
        return base + _EVT.LSB + num

class PublisherEvents(Const):
    """
    Events for Publisher class
    """

    class ALL(_EVT):
        """ALL Source Events"""

        EVENTS = 0
        POSITION = _EVT.get(EVENTS, 1)
        PANEL_UPDATE = _EVT.get(EVENTS, 2)
        SELECTED = _EVT.get(EVENTS, 3)

    class TASK(Const):
        """TASK Source Events"""

        EVENTS = 1
        PANEL_UPDATE = _EVT.get(EVENTS, 1)

    class TRACKER(Const):
        """TRACKER Source Events"""

        EVENTS = 2

    class NODE(Const):
        """NODE Source Events"""

        EVENTS = 4
        POSITION = _EVT.get(EVENTS, 1)
        SELECTED = _EVT.get(EVENTS, 2)

    class WIRE(Const):
        """WIRE Source Events"""

        EVENTS = 8

    class CURVE(Const):
        """CURVE Source Events"""

        EVENTS = 16
        SELECTED = _EVT.get(EVENTS, 1)

    class ALIGNMENT(Const):
        """ALIGNMENT Source Events"""

        EVENTS = 32

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

        if not isinstance(events, list):
            events = [events]

        for _i in self.event_indices:
            _result += [self.events[_i] for _e in events if _e & _i]
#            for _e in events:
#                if _e & _i:
#                    _result.append(self.events[_i])

        return _result

    def register(self, who, events, callback=None):
        """
        Callback registration for subscribers
        """
        print('\n{} registering {} on event {}'.format(self.id, who.name, events))
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

    def dispatch(self, event, message, verbose=False):
        """
        Message dispatch
        """

        #don't send empty messages
        if not message:
            return

        _list = self.get_subscribers(event)

        #for specific events, append subcribers to all events
        if event > 0:
            _list += self.get_subscribers(0)

        for _k, _v in self.events.items():
            print('\n\t', _k)
            print('\t', [_w.name for _w in _v])

        for _e in _list:
            for _k, _cb in _e.items():

                if verbose:
                    print('\n{}: notifying {} of message {} on event {}'\
                        .format(self.id, _k.name, message, event))

                _cb(event, message)
