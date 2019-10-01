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

from pivy import coin
from PySide.QtGui import QCursor

from ...support.singleton import Singleton

from .button_state import ButtonState
from .smart_tuple import SmartTuple

class MouseState(metaclass=Singleton):
    """
    Class to track the current state of the mouse based on
    passed Coin3D SoEvent parameters
    """

    def __init__(self):
        """
        MouseState construction
        """

        self.screen_position = ()
        self.world_position = ()

        self.button1 = ButtonState()
        self.button2 = ButtonState()
        self.button3 = ButtonState()
        self.buttons = [self.button1, self.button2, self.button3]

        self.alt_down = False
        self.ctrl_down = False
        self.shift_down = False

        self.vector = ()

        self.object = None
        self.component = ''

        self.state = [
            self.button1, self.button2, self.button3,
            self.world_position, self.screen_position
        ]

    def _update_button_state(self, arg, view_state):
        """
        Process mouse clicks
        """

        _btn = self.buttons[int(arg['Button'][-1]) - 1]
        _btn.pressed = arg['State'] == 'DOWN'

        #continue drag unless button is released
        if _btn.dragging:
            _btn.dragging = _btn.pressed

        #if button is still pressed and the position has changed,
        #begin drag operation
        elif _btn.pressed and (self.screen_position != _btn.screen_position):

            _btn.dragging = True
            _btn.drag_start = self.world_position

        else:
            _btn.drag_start = ()

        _btn.screen_position = self.screen_position
        _btn.world_position = self.world_position

    def _update_state(self, arg, view_state):
        """
        Update the positions and key states
        """

        self.screen_position = arg['Position']
        self.world_position = view_state.getPoint(self.screen_position)
        self.vector = self.world_position

        self.alt_down = arg['AltDown']
        self.ctrl_down = arg['CtrlDown']
        self.shift_down = arg['ShiftDown']

        if self.vector != self.world_position:
            self.vector = SmartTuple._sub(self.vector, self.world_position)

    def _update_component_state(self, info):
        """
        Update the component / object data
        """

        #clear state, no info exists
        if not info:

            self.object = None
            self.component = ''
            return

        self.object = info.get('Object')
        self.component = info.get('Component')

    def update(self, arg, view_state):
        """
        Update the current mouse state
        """

        _arg = arg

        if isinstance(arg, coin.SoEventCallback):
            _evt = arg.getEvent()
            _arg = {
                'Type': _evt.getTypeId().getName().getString(),
                'Time': float(_evt.getTime().getValue()),
                'Position': _evt.getPosition().getValue(),
                'ShiftDown': _evt.wasShiftDown(),
                'AltDown': _evt.wasAltDown(),
                'CtrlDown': _evt.wasCtrlDown()
            }

            if isinstance(_evt, coin.SoMouseButtonEvent):

                _arg['Button'] = 'BUTTON' + str(_evt.getButton())
                _arg['State'] = 'DOWN'

                if not _evt.isButtonPressEvent(_evt, _evt.getButton()):
                    _arg['State'] = 'UP'

        #update position/state information
        self._update_state(_arg, view_state)

        #process button events
        if _arg['Type'] == 'SoMouseButtonEvent':
            self._update_button_state(_arg, view_state)

        #return if dragging to preserve component / object data
        if self.button1.dragging:
            return

        self._update_component_state(
            view_state.getObjectInfo(self.screen_position))

    def set_mouse_position(self, view_state, coord):
        """
        Update the mouse cursor position independently
        """

        _new_pos = view_state.getPointOnScreen(coord)

        #set the mouse position at the updated screen coordinate
        _delta_pos = SmartTuple(_new_pos).sub(self.screen_position)

        #get screen position by adding offset to the new window position
        _pos = SmartTuple.from_values(_delta_pos[0], -_delta_pos[1])\
            .add(QCursor.pos().toTuple())

        QCursor.setPos(_pos[0], _pos[1])

        self.screen_position = _pos
        self.world_position = coord
