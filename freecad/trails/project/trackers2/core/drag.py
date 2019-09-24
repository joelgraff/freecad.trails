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

from .drag_state import DragState
from .mouse import Mouse

class Drag(Mouse):
    """
    Drag support for tracker objects
    """

    drag_state = DragState()

    #support for Geometry and Base without inheriting to permit non-drawable
    #trackers to have drag support
    geo_node = None
    name = ''
    view_state = None
    def copy(self, node=None): pass

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.is_dragging = False

        self.view_state.add_button_event(self.start_drag)

    def start_drag(self, so_event_cb):
        """
        Callback for start of drag operations
        """

        if not self.mouse_state.button1.dragging:
            return

        #copy the geo node ot the drag state
        self.drag_state.add_node(self.copy(self.geo_node))

        #leftover callback cleanup
        self.terminate_drag()

        #add drag events, set state
        self.view_state.add_mouse_event(self.on_drag)
        self.view_state.add_button_event(self.end_drag)

        self.drag_state.add_callbacks()
        #self.view_state.add_button_event(self.drag_state._end_drag_callback)
        #self.view_state.add_mouse_event(self.drag_state._on_drag_callback)

        self.is_dragging = True


    def on_drag(self, so_event_cb):
        """
        Callback for on-going drag operations
        """

        #leftover callback cleanup
        if not self.mouse_state.button1.dragging:
            self.terminate_drag()
            return

    def end_drag(self, so_event_cb):
        """
        Callback for terminating drag operations
        """

        _evt = so_event_cb.getEvent()

        if self.mouse_state.button1.dragging:
            return

        self.terminate_drag()

    def terminate_drag(self):
        """
        Remove mouse / button callbacks and clear state
        """

        #local object drag events
        self.view_state.remove_mouse_event(self.on_drag)
        self.view_state.remove_button_event(self.end_drag)

        #global drag state events
        #self.view_state.remove_button_event(self.drag_state._end_drag_callback)
        #self.view_state.remove_button_event(self.drag_state._on_drag_callback)

        self.is_dragging = False
