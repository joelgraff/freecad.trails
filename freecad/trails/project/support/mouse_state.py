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
            self.dragging = False
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
                'drag': self.dragging,
                'last': self.last,
                })

        def update(self, state, pos):
            """
            Update the button state
            """

            #update state on a state change only
            if state and (self.state != state):

                self.last = (self.state, self.pos)
                self.state = state
                self.pressed = state == 'DOWN'

                #assign position at down click
                if self.pressed:
                    self.pos = pos

            #true if button is down and state did not change before this call
            self.dragging = self.pressed and (self.pos != pos)

            if self.dragging:
                self.state = 'DRAG'

            self.pos = pos

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

        self.pos = App.Vector(_p + (0.0,))

        button = arg.get('Button')
        state = arg.get('State')
        buttons = []

        if button:
            buttons = [self.buttons[button]]

        #abort unless one or more buttons are pressed
        if not buttons or not state:
            buttons = [_x for _x in self.buttons.values() if _x.pressed]

        if not buttons:
            return

        for _btn in buttons:
            _btn.update(state, self.pos)

        self.state = [self.buttons, self.pos]
