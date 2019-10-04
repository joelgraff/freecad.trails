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
Drag class for Tracker objects
"""

from ...support.singleton import Singleton

#from .drag_state import DragState
from .base import Base

class DragGlobalCallbacks(metaclass=Singleton):
    """
    Class to track the current state of the active or specified view
    """

    #Base prototypes
    base = None

    def __init__(self, view_state):
        """
        Constructor
        """

        self.callbacks = {}

        #self.callbacks[coin.SoMouseButtonEvent] =\
        #    DragState().drag_event_callback.add

        #DragState().add_mouse_event(self.on_drag_callback)
        #DragState().add_button_event(self.end_drag_callback)

        #self.base.insert_node(DragState().drag_switch)

    def on_drag_callback(self, so_event_cb):
        """
        Class-level callback to update the drag state transform as a
        mouse event
        """
        print('drag_state on drag')

        #if not DragState().start:
        #    DragState().start = Mouse.mouse_state.button1.world_position

        #if Mouse.mouse_state.alt_down:
        #    DragState().rotate(Mouse.mouse_state.world_position)

        #else:
        #    DragState().translate(Mouse.mouse_state.world_position)

    def end_drag_callback(self, so_event_cb):
        """
        Class-level callback to reset drag state at end of drag operation
        """

        _evt = so_event_cb.getEvent()

        print(
            _evt.getButton(), _evt.isButtonPressEvent(_evt, 1),
            _evt.getPosition().getValue()
        )
        #if Mouse.mouse_state.button1.dragging:
        #    return

        print('drag state end drag')
        self.terminate_callbacks()

        #DragState().reset()

    def terminate_callbacks(self):
        """
        Cleanup event callbacks
        """

        Base.view_state.remove_button_event(self.end_drag_callback)
        Base.view_state.remove_mouse_event(self.on_drag_callback)

class Drag():
    """
    Drag support for tracker objects
    """
    #drag_state = DragState()

    #support for Geometry and Base without inheriting to permit non-drawable
    #trackers to have drag support
    geo_node = None
    name = ''
    view_state = None

    def copy(self, node=None): """prototype"""; pass

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.is_dragging = False
        #DragGlobalCallbacks()

    def start_drag(self, so_event_cb):
        """
        Callback for start of drag operations
        """

        #if not self.mouse_state.button1.dragging:
        #    return

        #copy the geo node ot the drag state
        #self.drag_state.add_node(self.copy(self.geo_node))

        #leftover callback cleanup
        self.terminate_drag()

        #add drag events, set state
        self.view_state.add_mouse_event(self.on_drag)
        self.view_state.add_button_event(self.end_drag)

        self.is_dragging = True


    def on_drag(self, so_event_cb):
        """
        Callback for on-going drag operations
        """

        #leftover callback cleanup
        #if not self.mouse_state.button1.dragging:
        #    self.terminate_drag()
        #    return

    def end_drag(self, so_event_cb):
        """
        Callback for terminating drag operations
        """

        _evt = so_event_cb.getEvent()

        #if self.mouse_state.button1.dragging:
        #    return

        self.terminate_drag()

    def terminate_drag(self):
        """
        Remove mouse / button callbacks and clear state
        """

        #local object drag events
        self.view_state.remove_mouse_event(self.on_drag)
        self.view_state.remove_button_event(self.end_drag)

        #global drag state events
        #self.view_state.remove_button_event
        #(self.drag_state._end_drag_callback)
        #self.view_state.remove_button_event(self.drag_state._on_drag_callback)

        self.is_dragging = False
