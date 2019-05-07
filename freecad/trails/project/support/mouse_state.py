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
Useful mosue support functions
"""
import FreeCAD as App

class MouseState():
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
            self.pos = App.Vector()
            self.drag = False
            self.last = ''

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
                'drag': self.drag,
                'last': self.last,
                })

        def update(self, state, pos):
            """
            Update the button state
            """

            self.last = self.state
            self.pos = pos
            self.state = state
            self.pressed = state == 'DOWN'

    def __init__(self):
        """
        MouseState construction
        """

        self.pos = App.Vector()
        self.last = ''

        self.buttons = {
            'BUTTON1': self.ButtonState(),
            'BUTTON2': self.ButtonState(),
            'BUTTON3': self.ButtonState(),
        }

        self.button1 = self.buttons['BUTTON1']
        self.button2 = self.buttons['BUTTON2']
        self.button3 = self.buttons['BUTTON3']

        self.state = [self.buttons, self.pos]

    def update(self, arg, _p):
        """
        Update the current mouse state
        """

        if _p:
            self.pos = App.Vector(_p + (0.0,))

        if not arg or not _p:
            return

        button = arg.get('Button')
        state = arg.get('State')

        if not button or not state:
            return

        _btn = self.buttons[button]

        #test for drag if not already set
        if not _btn.drag:
            if _btn.state == 'DOWN':
                _btn.drag = self.pos.distanceToPoint(_btn.pos) >= 1.0
                _btn.state = 'DRAG'

        old_pos = _btn.pos

        self.buttons[button].update(state, self.pos)

        self.last = [button, _btn.last, old_pos]
