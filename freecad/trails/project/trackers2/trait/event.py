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
import weakref

from ..support.smart_tuple import SmartTuple

from .coin.coin_group import CoinGroup
from .coin.coin_enums import NodeTypes as Nodes
from .coin.coin_enums import MouseEvents as MouseEvents
from .coin import coin_utils

#from ..support.publisher_events import PublisherEvents as SignalEvents

class Event():
    """
    Event Callback traits.
    """

    #Base prototypes
    base = None
    view_state = None
    mouse_state = None
    name = ''
    def get_path(self, node, parent=None): """prototype"""; pass

    _self_weak_list = []
    _default_callback_node = None

    @staticmethod
    def set_paths():
        """
        Static class method for setting paths on registered callbacks after
        scene insertion.
        """

        for _v in Event._self_weak_list:
            _v().set_event_paths()

    def __init__(self):
        """
        Constructor
        """

        self.event = CoinGroup(
            switch_first=True, is_separator=False, is_switched=True,
            parent=self.base, name=self.name + '__EVENTS')

        self.event.callbacks = []
        self.callbacks = []

        self.path_nodes = []

        #create a global callback for managing mouse updates
        if not Event._default_callback_node:

            self.add_mouse_event(self._event_mouse_event)
            self.add_button_event(self._event_button_event)
            Event._default_callback_node = self.event.callbacks[0]

        self.event.set_visibility(True)

        Event._self_weak_list.append(weakref.ref(self))

        super().__init__()

    def _event_mouse_event(self, data, event_cb):
        """
        Default mouse location event
        """

        _last_pos = SmartTuple(self.mouse_state.world_position)

        self.mouse_state.update(event_cb, self.view_state)

        if not (self.mouse_state.shift_down and \
            self.mouse_state.button1.dragging):

        #    self.mouse_state.shift_down \
        #    and _last_pos._tuple \
        #    and self.mouse_state.vector.Length \
        #    and self.mouse_state.button1.dragging):

            return

        _vec = SmartTuple(self.mouse_state.vector).normalize(0.10)
        _new_pos = _last_pos.add(_vec)._tuple

        self.mouse_state.set_mouse_position(self.view_state, _new_pos)


    def _event_button_event(self, data, event_cb):
        """
        Default button event
        """

        self.mouse_state.update(event_cb, self.view_state)

    def add_event_callback_node(self):
        """
        Add an event callback node to the current group
        """

        self.event.callbacks.append(
            self.event.add_node(Nodes.EVENT_CB, 'EVENT_CALLBACK')
        )

        self.callbacks.append({})

    def remove_event_callback_node(self, node):
        """
        Remove an event callback node from the current group
        """

        if node not in self.event.callbacks:
            return

        self.event.remove_node(node)

        _index = self.event.callbacks.index(node)

        del self.event.callbacks[_index]
        del self.callbacks[_index]

    def set_event_paths(self):
        """
        Set the specified path on the event callback at the specified index
        """

        if not self.path_nodes:
            return

        if len(self.event.callbacks) < len(self.path_nodes):
            return

        for _i, _node in enumerate(self.path_nodes):
            _node = self.path_nodes[_i]
            _sa = coin_utils.search(_node, self.view_state.sg_root)
            self.event.callbacks[_i].setPath(_sa.getPath())

    def add_event_callback(self, event_type, callback, index=-1):
        """
        Add an event callback
        """

        #if none exist, add a new one
        #otherwise default behavior reuses last-created SoEventCb node
        if not self.event.callbacks:
            print(self.name, 'adding event cb node')
            self.add_event_callback_node()

        _et = event_type.getName().getString()

        if not _et in self.callbacks:
            self.callbacks[index][_et] = {}

        _cbs = self.callbacks[index][_et]

        if callback in _cbs:
            return

        _cbs[callback] = \
            self.event.callbacks[index].addEventCallback(event_type, callback)

    def remove_event_callback(self, event_type, callback, index=-1):
        """
        Remove an event callback
        """

        _et = event_type.getName().getString()

        if _et not in self.callbacks:
            return

        _cbs = self.callbacks[index][_et]

        if callback not in _cbs:
            return

        self.event.callbacks[index].removeEventCallback(
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

        return self.event.whichChild == 0

    def toggle_event_callbacks(self):
        """
        Switch event callbacks on / off
        """
        #PyLint doesn't detect getValue()
        #pylint: disable=no-member

        if self.event.whichChild.getValue() == 0:
            self.event.whichChild = -1

        else:
            self.event.whichChild = 0

    def set_event_path(self, event_type, message, verbose=False, node=None):
        """
        Add / remove path for event callbacks
        """

        if node is None:
            node = self.base.path_node

        if node is None:
            self.event.callback.setPath(self.base.path_node)
            return

        self.event.callback.setPath(self.base.path_node(node))
