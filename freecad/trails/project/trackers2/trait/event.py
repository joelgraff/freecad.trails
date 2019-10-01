# -*- coding: utf-8 -*-
#**************************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
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
Event class for Tracker objects
"""

from .coin.coin_group import CoinGroup
from .coin.coin_enums import CoinNodes as Nodes
from .coin.coin_enums import MouseEvents as MouseEvents

from ..support.publisher_events import PublisherEvents as SignalEvents

class Event():
    """
    Event Callback traits.
    """

    #Base prototypes
    base = None
    name = ''
    def register(self, who, events, callback=None): """Prototype"""; pass

    def __init__(self):
        """
        Constructor
        """

        self.events = CoinGroup(
            is_separator=False, is_switched=True,
            parent=self.base, name=self.name + '__EVENTS')

        self.events.callback = \
            self.events.add_node(Nodes.EVENT_CB, '__EVENT_CALLBACK')

        self.events.root.whichChild = 0

        self.callbacks = {}

        self.register(
            self, SignalEvents.GEOMETRY.APPLY_PATHING, self.set_event_path)

        self.events.set_visibility(True)
        super().__init__()

    def add_event_callback(self, event_type, callback):
        """
        Add an event callback
        """

        _et = event_type.getName().getString()

        if not _et in self.callbacks:
            self.callbacks[_et] = {}

        _cbs = self.callbacks[_et]

        if callback in _cbs:
            return

        _cbs[callback] = \
            self.events.callback.addEventCallback(event_type, callback)

    def remove_event_callback(self, event_type, callback):
        """
        Remove an event callback
        """

        _et = event_type.getName().getString()

        if _et not in self.callbacks:
            return

        _cbs = self.callbacks[_et]

        if callback not in _cbs:
            return

        self.events.callback.removeEventCallback(
            event_type, _cbs[callback])

        del _cbs[callback]

    def add_mouse_event(self, callback):
        """
        Convenience function
        """

        self.add_event_callback(MouseEvents.LOCATION2, callback)

    def add_button_event(self, callback):
        """
        Convenience function
        """

        self.add_event_callback(MouseEvents.MOUSE_BUTTON, callback)

    def remove_mouse_event(self, callback):
        """
        Convenience function
        """

        self.remove_event_callback(MouseEvents.LOCATION2, callback)

    def remove_button_event(self, callback):
        """
        Convenience function
        """

        self.remove_event_callback(MouseEvents.MOUSE_BUTTON, callback)

    def events_enabled(self):
        """
        Returns whether or not event switch is on
        """

        return self.events.whichChild == 0

    def toggle_event_callbacks(self):
        """
        Switch event callbacks on / off
        """
        #PyLint doesn't detect getValue()
        #pylint: disable=no-member

        if self.events.whichChild.getValue() == 0:
            self.events.whichChild = -1

        else:
            self.events.whichChild = 0

    def set_event_path(self, event_type, message, verbose=False, node=None):
        """
        Add / remove path for event callbacks
        """

        if node is None:
            node = self.base.path_node

        if node is None:
            self.events.callback.setPath(self.base.path_node)
            return

        self.events.callback.setPath(self.base.path_node(node))
