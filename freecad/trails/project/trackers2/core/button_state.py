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
Mouse button state tracking
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
