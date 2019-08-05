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
        self.translate_transform = coin.SoTransform()
        self.translate_transform.translation.setValue(
            tuple([0.0, 0.0, 0.0])
        )

        self.rotate_transform = coin.SoTransform()

        self.node = None
        self.matrix = None

        self.drag_line_coord = coin.SoCoordinate3()

        self._build_drag_line()

        self.group.addChild(self.translate_transform)
        self.group.addChild(self.rotate_transform)

        self.drag_node = None

        self.delta = Vector()
        self.coordinates = Vector()
        self.offset = Vector()
        self.start_pos = tuple()

        self.angle = 0.0
        self.rotation_center = Vector()
        self.rotation = 0.0

        self.sg_ok = False
        self.sg_root = None

    def update(self, start = None):
        """
        Update the drag line
        """

        if start is None:
            start = self.start

        _p = [tuple(start), tuple(self.coordinates)]

        self.drag_line_coord.point.setValues(0, 2, _p)

    def _build_drag_line(self):
        """
        Build the drag line for drag operations
        """

        _m = coin.SoMarkerSet()
        _l = coin.SoLineSet()
        _g = coin.SoSeparator()

        _g.addChild(self.drag_line_coord)
        _g.addChild(_m)
        _g.addChild(_l)
        _l.numVertices.setValue(2)

        self.group.addChild(_g)

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
