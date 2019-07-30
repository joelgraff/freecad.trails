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
from .view_state import ViewState

class DragState(metaclass=Singleton):
    """
    Class to track the current state of the active or specified view
    """

    def __init__(self):

        self.start = Vector()

        self.group = coin.SoSeparator()
        self.transform = coin.SoTransform()

        self.node = None
        self.matrix = None
        self.group.addChild(self.transform)

    def add_node(self, node):
        """
        Add a node to the drag node group
        """

        self.group.addChild(node)

    def finish(self):
        """
        Return the transformation matrix for the provided node
        """

        if not self.node:
            return

        self.node.remove_node(self.group)

        #abort if no children have been added
        if self.group.getNumChildren() < 2:
            return None

        #define the search path
        _search = coin.SoSearchAction()
        _search.setNode(self.group.getChild(1))
        _search.apply(ViewState().sg_root)

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(ViewState().viewport)
        _matrix.apply(_search.getPath())

        self.reset()

        self.matrix = _matrix.getMatrix()

    def reset(self):
        """
        State reset function
        """

        self.group.removeAllChildren()

        self.__init__()
