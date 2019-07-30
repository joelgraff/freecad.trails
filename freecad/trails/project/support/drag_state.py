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
Drag state class
"""

from pivy import coin

from FreeCAD import Vector

from .singleton import Singleton

class DragState(metaclass=Singleton):
    """
    Class to track the current state of the active or specified view
    """

    def __init__(self):

        self.start_coord = Vector()
        self.start_pos = tuple()

        self.node_group = coin.SoSeparator()
        self.transform = coin.SoTransform()

        self.drag_node = None

        self.node_group.addChild(self.transform)

    def add_node(self, node):
        """
        Add a node to the drag node group
        """

        self.node_group.addChild(node)

    def reset(self):
        """
        State reset function
        """

        self.node_group.removeAllChildren()
        self.__init__()
