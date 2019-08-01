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

from DraftGui import todo

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
        self.transform.translation.setValue(
            tuple([0.0, 0.0, 0.0])
        )

        self.node = None
        self.matrix = None
        self.group.addChild(self.transform)
        self.drag_node = None

        self.sg_ok = False
        self.sg_root = None

    def add_node(self, node):
        """
        Add a node to the drag node group
        """

        if not self.drag_node:
            self.drag_node = node

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

        ViewState().get_matrix(self.group.getChild(1))

        self.reset()

    @staticmethod
    def _insert(drag_state):
        """
        Delayed callback for sg_ok
        """

        drag_state.sg_root.insertChild(drag_state.group, 0)
        drag_state.sg_ok = True

    def insert(self):
        """
        Custom function to manage drag state insertion and provide
        flag when scenegraph has been updated
        """

        self.sg_ok = False

        self.sg_root = ViewState().sg_root
        todo.delay(DragState()._insert, DragState())


    def reset(self):
        """
        State reset function
        """

        self.group.removeAllChildren()

        self.__init__()
