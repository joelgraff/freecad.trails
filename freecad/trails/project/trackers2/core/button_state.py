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
        self.pressed = False
        self.screen_position = ()
        self.world_position = ()
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
            'pressed': self.pressed,
            'screen position': self.screen_position,
            'world position': self.world_position,
            'dragging': self.dragging,
            'drag start': self.drag_start
            })
