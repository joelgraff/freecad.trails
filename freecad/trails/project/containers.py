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
Tracker for drag data
"""

from FreeCAD import Vector

class DragState():
    """
    State tracker for drag operations
    """
    def __init__(self):
        """
        Constructor
        """

        self.start = None
        self.center = None
        self.rotation = None
        self.position = None
        self.angle = 0.0
        self.translation = Vector()
        self.multi = False
        self.curves = []
        self.nodes = []
        self.node_idx = []
        self.tracker_state = []

    def reset(self):
        """
        Reset the object to defaults
        """

        self.__init__()