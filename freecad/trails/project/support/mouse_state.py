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

from .singleton import Singleton

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
                self.pressed = state == 'DOWN'

                #assign position at down click
                if self.pressed:
                    self.pos = pos

            #if we're already dragging, continue only if the button
            #hasn't been released
            if self.dragging:
                self.dragging = self.pressed and (self.state != 'UP')

            #otherwise, start only if the button is pressed and the
            #mouse has moved
            else:
                if self.pressed and (self.pos != pos):
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

        self.drag_start = ()

        self.state = [self.buttons, self.pos]

    def update(self, arg, _p):
        """
        Update the current mouse state
        """

        self.pos = _p + (0.0,)

        button = arg.get('Button')
        state = arg.get('State')
        buttons = []

        #define button list and update pressed state
        if button:
            self.buttons[button].pressed = (state != 'UP')
            buttons = [self.buttons[button]]

        #abort unless one or more buttons are pressed
        if not buttons or not state:
            buttons = [_x for _x in self.buttons.values() if _x.pressed]

        #if still no button state, abort
        if not buttons:
            return

        for _btn in buttons:
            _btn.update(state, self.pos)


        #self.state = [self.buttons, self.pos, self.drag_start]
