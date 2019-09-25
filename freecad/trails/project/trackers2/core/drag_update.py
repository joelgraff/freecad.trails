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
Drag state class updater
"""

from ...support.singleton import Singleton

from .base import Base
from .view_state import ViewState
from .mouse_state import MouseState
from .drag_state import DragState

class DragUpdate(Base, metaclass=Singleton):
    """
    Class to track the current state of the active or specified view
    """

    def __init__(self):
        """
        Constructor
        """

        self.insert_node(DragState().drag_switch)

    def add_callbacks(self):

        ViewState().add_button_event(self._end_drag_callback)
        ViewState().add_mouse_event(self._on_drag_callback)

    def _on_drag_callback(self, so_event_cb):
        """
        Class-level callback to update the drag state transform as a 
        mouse event
        """
        print('drag_state on drag')

        if not DragState().start:
            DragState().start = MouseState().button1.world_position

        if MouseState().alt_down:
            DragState().rotate(MouseState().world_position)

        else:
            DragState().translate(MouseState().world_position)

    def _end_drag_callback(self, so_event_cb):
        """
        Class-level callback to reset drag state at end of drag operation
        """

        _evt = so_event_cb.getEvent()

        print(_evt.getButton(), _evt.isButtonPressEvent(_evt, 1), _evt.getPosition().getValue())
        if MouseState().button1.dragging:
            return

        print('drag state end drag')
        self.terminate_callbacks()

        DragState().reset()

    def terminate_callbacks(self):
        """
        Cleanup event callbacks
        """

        ViewState().remove_button_event(self._end_drag_callback)
        ViewState().remove_mouse_event(self._on_drag_callback)