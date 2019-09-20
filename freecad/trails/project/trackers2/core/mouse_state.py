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

from operator import sub, add

from PySide.QtGui import QCursor

from ...support.singleton import Singleton

from .button_state import ButtonState

from .smart_tuple import SmartTuple

class MouseState(metaclass=Singleton):
    """
    Class to track the current state of the mouse based on
    passed Coin3D SoEvent parameters
    """

    tuple_sub = lambda lhs, rhs: tuple(map(sub, lhs, rhs))
    tuple_add = lambda lhs, rhs: tuple(map(add, lhs, rhs))

    def __init__(self):
        """
        MouseState construction
        """

        self.pos = ()

        self.buttons = {
            'BUTTON1': ButtonState(),
            'BUTTON2': ButtonState(),
            'BUTTON3': ButtonState(),
        }

        self.button1 = self.buttons['BUTTON1']
        self.button2 = self.buttons['BUTTON2']
        self.button3 = self.buttons['BUTTON3']

        self.altDown = False
        self.ctrlDown = False
        self.shiftDown = False

        self.object = ''
        self.component = ''
        self.coordinates = (0.0, 0.0, 0.0)
        self.last_coord = (0.0, 0.0, 0.0)
        self.last_pos = ()
        self.vector = ()

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

    def update(self, arg, view_state):
        """
        Update the current mouse state
        """

        _pos = view_state.getCursorPos()
        _coord = self.coordinates

        if _pos != self.pos:
            self.last_pos = self.pos
            self.set_position(_pos)
            _coord = None

        _info = view_state.getObjectInfo(self.pos)

        if not _coord:
            _coord = view_state.getPoint(self.pos)

        _btn = arg.get('Button')
        _state = arg.get('State')

        self.altDown = arg['AltDown']
        self.ctrlDown = arg['CtrlDown']
        self.shiftDown = arg['ShiftDown']

        self.vector = SmartTuple(_coord).sub(self.last_coord)

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

            _coord = (_info['x'], _info['y'], _info['z'])

        #preserve the selected component at the start of drag operation
        elif self.component and not self.button1.dragging:

            self.object = ''
            self.component = ''

        self.last_coord = self.coordinates
        self.coordinates = _coord

    def set_mouse_position(self, view_state, coord):
        """
        Update the mouse cursor position independently
        """

        _new_pos = view_state.getPointOnScreen(coord)

        #set the mouse position at the updated screen coordinate
        _delta_pos = SmartTuple(_new_pos).sub(self.pos)

        #get screen position by adding offset to the new window position
        _pos = SmartTuple.from_values(_delta_pos[0], -_delta_pos[1])\
            .add(QCursor.pos().toTuple())

        QCursor.setPos(_pos[0], _pos[1])

        self.coordinates = SmartTuple(coord)._tuple
        self.set_position(_new_pos)
