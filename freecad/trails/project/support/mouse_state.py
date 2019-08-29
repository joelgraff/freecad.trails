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
Mouse state class
"""

from FreeCAD import Vector

from PySide.QtGui import QCursor

from .singleton import Singleton
from .view_state import ViewState

class MouseState(metaclass=Singleton):
    """
    Class to track the current state of the mouse based on
    passed Coin3D SoEvent parameters
    """

    class ButtonState():
        """
        Internal class to track button state
        """
        def __init__(self):
            """
            ButtonState constructor
            """
            self.state = ''
            self.pressed = False
            self.pos = ()
            self.dragging = False
            self.drag_start = ()

        def reset(self):
            """
            Reset button parameters
            """

            self.__init__()

        def __str__(self):
            """
            Button string representation
            """

            return self.__repr__()

        def __repr__(self):
            """
            Button string representation
            """

            return str({
                'state': self.state,
                'pressed': self.pressed,
                'pos': self.pos,
                'dragging': self.dragging,
                'drag start': self.drag_start
                })

        def update(self, state, pos):
            """
            Update the button state
            """

            #update state on a state change only
            if state and (self.state != state):

                self.state = state
                self.pressed = state != 'UP'

                #assign position at down click
                if self.pressed and not self.pos:
                    self.pos = pos

            #if we're already dragging, continue only if the button
            #hasn't been released
            if self.dragging:
                self.dragging = self.pressed

            #otherwise, start only if the button is pressed and the
            #mouse has moved
            elif self.pressed and (self.pos != pos):

                self.dragging = True
                self.drag_start = pos

            if self.dragging:
                self.state = 'DRAG'

            else:
                self.drag_start = ()

            self.pos = pos

    def __init__(self):
        """
        MouseState construction
        """

        self.pos = ()

        self.buttons = {
            'BUTTON1': self.ButtonState(),
            'BUTTON2': self.ButtonState(),
            'BUTTON3': self.ButtonState(),
        }

        self.button1 = self.buttons['BUTTON1']
        self.button2 = self.buttons['BUTTON2']
        self.button3 = self.buttons['BUTTON3']

        self.altDown = False
        self.ctrlDown = False
        self.shiftDown = False

        self.object = ''
        self.component = ''
        self.coordinates = Vector()
        self.last_coord = Vector()
        self.last_pos = ()
        self.vector = Vector()

        self.state = [self.buttons, self.pos]

    def set_position(self, pos):
        """
        Set the position as a two-value tuple
        """

        _p = pos

        if len(_p) < 2:
            return

        if not isinstance(_p, tuple):
            _p = tuple(pos)

        if len(_p) > 2:
            _p = _p[0:2]

        self.pos = _p

    def update(self, arg, position):
        """
        Update the current mouse state
        """

        _pos = position
        _coord = self.coordinates

        if _pos != self.pos:
            self.last_pos = self.pos
            self.set_position(_pos)
            _coord = None

        _info = ViewState().view.getObjectInfo(self.pos)

        if not _coord:
            _coord = ViewState().view.getPoint(self.pos)

        _btn = arg.get('Button')
        _state = arg.get('State')

        self.altDown = arg['AltDown']
        self.ctrlDown = arg['CtrlDown']
        self.shiftDown = arg['ShiftDown']
        self.vector = _coord.sub(self.last_coord)

        _b_list = self.buttons.values()

        if _btn:
            _b_list = [self.buttons[_btn]]

        for _v in _b_list:
            _v.update(_state, self.pos)

        if _info:

            if not self.button1.dragging:

                self.object = _info['Object']
                self.component = _info.get('Component')

            if self.component is None:
                self.component = ''

            _coord = Vector(_info['x'], _info['y'], _info['z'])

        #preserve the selected component at the start of drag operation
        elif self.component and not self.button1.dragging:

            self.object = ''
            self.component = ''

        self.last_coord = self.coordinates
        self.coordinates = _coord

    def get_drag_vector(self, world=False):
        """
        Return the drag vector pointing toward the current position from
        the point where drag operations began
        """

        _result = Vector()

        if not self.button1.dragging:
            return _result

        return Vector(self.pos).sub(Vector(self.button1.drag_start))

    def set_mouse_position(self, coord):
        """
        Update the mouse cursor position independently
        """

        _new_pos = ViewState().getPointOnScreen(coord)

        #set the mouse position at the updated screen coordinate
        _delta_pos = _new_pos.sub(Vector(self.pos + (0.0,)))

        #get screen position by adding offset to the new window position
        _pos = Vector(QCursor.pos().toTuple() + (0.0,)).add(
            Vector(_delta_pos.x, -_delta_pos.y))

        QCursor.setPos(_pos[0], _pos[1])

        self.coordinates = Vector(coord)
        self.set_position(_new_pos)
