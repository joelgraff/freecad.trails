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
Base class for Tracker objects
"""
import weakref

from pivy import coin

from DraftGui import todo

from .view_state import ViewState
from .publisher import Publisher
from .publisher_events import PublisherEvents as Events
from .subscriber import Subscriber

#from ...containers import TrackerContainer

class Base(Publisher, Subscriber):
    """
    Base class for Tracker objects
    """

    #global view statge singleton
    view_state = None

    pathed_trackers = []

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #'virtual' function declarations overriden by class inheritance
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #Style
    def set_style(self, style=None, draw=None, color=None): 
        """prototype"""; pass

    def __init__(self, name):
        """
        Constructor
        """

        #name is three parts, delimited by periods ('doc.task.obj')
        #object name is always first
        self.names = name.split('.')[::-1]
        self.name = self.names[0]

        #pad array to ensure three elements
        if len(self.names) < 3:
            self.names += ['']*(3-len(self.names))

        if not Base.view_state:
            Base.view_state = ViewState()

        self.sg_root = self.view_state.sg_root

        self.callbacks = {}

        self.base_path_node = None
        self.base_switch = coin.SoSwitch()

        self.base_node = coin.SoSeparator()
        self.base_transform = coin.SoTransform()

        self.base_event_switch = coin.SoSwitch()
        self.base_event_cb = coin.SoEventCallback()
        self.base_event_switch.addChild(self.base_event_cb)
        self.base_event_switch.whichChild = 0

        self.base_picker = coin.SoPickStyle()

        self.base_node.addChild(self.base_event_switch)
        self.base_node.addChild(self.base_transform)
        self.base_node.addChild(self.base_picker)

        self.base_switch.addChild(self.base_node)
        self.set_visibility()

        #add to the global statick list of all subscribers for the
        #Publsiher class.  Weak-referenced to facilitate cleanup
        Publisher.all_subscribers.append(weakref.WeakMethod(self.notify_all))

        super().__init__()

    def insert_into_scenegraph(self):
        """
        Insert the base node into the scene graph and trigger notifications
        """

        self.insert_node(self.base_node)
        todo.delay(self.dispatch_all, Events.GEOMETRY.APPLY_PATHING)

    def notify_all(self, event_type, message, verbose=False):
        """
        Override base notify_all()
        """

        super().notify_all(event_type, message, verbose)

        if event_type == Events.GEOMETRY.APPLY_PATHING:
            print(self.name, 'notifying...')
            self.set_event_path()

    def notify(self, event_type, message, verbose=False):
        """
        Override base notfy()
        """

        super().notify(event_type, message, verbose)

    def copy(self, node=None):
        """
        Return a copy of the tracker node
        """

        #copy operation assumes the geometry should not be controlled
        #by the node switch.  To copy with switch, call copy(self.get_node())
        if not node:
            node = self.base_node

        return node.copy()

    def insert_node(self, node, parent=None, index=None):
        """
        Insert a node as a child of the passed node
        """

        _idx = index

        _fn = None

        if not parent:
            if _idx is None:
                _idx = 0

            _fn = lambda _x: self.sg_root.insertChild(_x, _idx)

        elif _idx is not None:
            _fn = lambda _x: parent.insertChild(_x, _idx)

        else:
            _fn = parent.addChild

        todo.delay(_fn, node)

    def remove_node(self, node, parent=None):
        """
        Convenience wrapper for _remove_node
        """

        if not parent:
            parent = self.sg_root

        if parent.findChild(node) >= 0:
            todo.delay(parent.removeChild, node)

    def set_visibility(self, visible=True):
        """
        Update the tracker visibility
        """

        if visible:
            self.base_switch.whichChild = 0

        else:
            self.base_switch.whichChild = -1

    def is_visible(self):
        """
        Return the visibility of the tracker
        """
        #pylint: disable=no-member
        return self.base_switch.whichChild.getValue() == 0

    def set_pick_style(self, is_pickable):
        """
        Set the selectability of the node using the SoPickStyle node
        """

        _state = coin.SoPickStyle.UNPICKABLE

        if is_pickable:
            _state = coin.SoPickStyle.SHAPE

        self.base_picker.style.setValue(_state)

    def is_pickable(self):
        """
        Return a bool indicating whether or not the node may be selected
        """

        return self.base_picker.style.getValue() != coin.SoPickStyle.UNPICKABLE

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
            self.base_event_cb.addEventCallback(event_type, callback)

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

        self.base_event_cb.removeEventCallback(event_type, _cbs[callback])

        del _cbs[callback]

    def events_enabled(self):
        """
        Returns whether or not event switch is on
        """

        return self.base_event_switch.whichChild == 0

    def toggle_event_callbacks(self):
        """
        Switch event callbacks on / off
        """
        #pylint: disable=no-member
        if self.base_event_switch.whichChild.getValue() == 0:
            self.base_event_switch.whichChild = -1

        else:
            self.base_event_switch.whichChild = 0

    def set_event_path(self, node=None):
        """
        Add / remove path for event callbacks
        """

        if node is None:
            node = self.base_path_node

        if node is None:
            self.base_event_cb.setPath(self.base_path_node)
            return

        _sa = coin.SoSearchAction()
        _sa.setNode(node)
        _sa.apply(self.view_state.sg_root)

        self.base_event_cb.setPath(_sa.getPath())

    def finalize(self, node=None, parent=None):
        """
        Node destruction / cleanup
        """

        if node is None:
            node = self.base_node

        self.remove_node(node, parent)
