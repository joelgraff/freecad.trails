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
            elif self.pressed and (self.pos != pos):
                    print('start drag!')
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

        self.state = [self.buttons, self.pos]

    def update(self, arg, _p):
        """
        Update the current mouse state
        """

        self.pos = _p + (0.0,)

        _btn = arg.get('Button')
        _state = arg.get('State')

        if not _state:
            return

        if not _btn:
            return

        _btn = self.buttons[_btn]

        if _btn.state == _state:
            return

        _btn.pressed = _state == 'DOWN'
        _btn.state = _state

        #drag condition depends on whether drag ops are only starting or 
        #continuing.  If only starting, drag does not begin unil button is
        #pressed and mouse moves.  If continuing, drag ends when button is up
        if _btn.dragging:
            _btn.dragging = _btn.pressed and (_btn.state != 'UP')
        else:
            _btn.dragging = _btn.pressed and (_btn.drag_start != self.pos)

        #set drag states
        if _btn.dragging:
            _btn.drag_start = self.pos
            _btn.state = 'DRAG'

        else:
            _btn.drag_start = ()

    def get_drag_vector(self):
        """
        Return the drag vector pointing toward the current position from the point where drag operations began
        """

        if not self.button1.dragging:
            return Vector()

        return Vector(self.pos).sub(Vector(self.button1.drag_start))