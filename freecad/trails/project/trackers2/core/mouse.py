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
Mouse services for Tracker objects
"""

from ...support.singleton import Singleton

from .mouse_state import MouseState
from .smart_tuple import SmartTuple

class MouseGlobalCallbacks(metaclass=Singleton):
    """
    Global mouse-handling callbacks for the view level
    """
    def __init__(self, view_state):
        """
        Constructor
        """

        self.view_state = view_state
        
        self.view_state.add_mouse_event(self.global_mouse_event)
        self.view_state.add_button_event(self.global_button_event)

    def global_mouse_event(self, arg):
        """
        Global SoLocation2 Event callback
        """

        _last_pos = SmartTuple(MouseState().world_position)

        MouseState().update(arg, self.view_state)

        if not (MouseState().shift_down and _last_pos._tuple\
            and MouseState().vector.Length):

            return

        _vec = SmartTuple(MouseState().vector).normalize(0.10)
        _new_pos = _last_pos.add(_vec)._tuple

        MouseState().set_mouse_position(self.view_state, _new_pos)

    def global_button_event(self, arg):
        """
        Global SoMouseButtonEvent callback
        """

        MouseState().update(arg, self.view_state)

class Mouse():
    """
    Mouse services for Tracker objects
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Prototypes
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #Base
    view_state = None
    def add_event_callback(self, event_type, callback): """prototype"""; pass

    mouse_state = None
    mouse_global_callbacks = None

    def __init__(self):
        """
        Constructor
        """

        if not Mouse.mouse_state:
            Mouse.mouse_state = MouseState()

        if not Mouse.mouse_global_callbacks:
            Mouse.mouse_global_callbacks = \
                MouseGlobalCallbacks(self.view_state)

        self.add_event_callback(
            self.mouse_state.Events.LOCATION2, self.mouse_event)

        self.add_event_callback(
            self.mouse_state.Events.MOUSE_BUTTON, self.button_event)

        super().__init__()

    def mouse_event(self, user_data, event_cb):
        """
        Base mouse event implementation
        """
        pass

    def button_event(self, user_data, event_cb):
        """
        Base button event implementation
        """
        pass
