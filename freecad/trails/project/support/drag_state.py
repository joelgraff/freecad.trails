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
        self.node_group = coin.SoSeparator()

        self.partial_coords = []
        self.partial_indices = []

        self.translate_transform = coin.SoTransform()
        self.translate_transform.translation.setValue(
            tuple([0.0, 0.0, 0.0])
        )

        self.rotate_transform = coin.SoTransform()

        self.node = None

        self.drag_line_coord = coin.SoCoordinate3()

        self._build_drag_line()

        self.group.addChild(self.translate_transform)
        self.group.addChild(self.rotate_transform)
        self.group.addChild(self.node_group)

        self.drag_node = None

        self.abort = False

        #coordinate tracking properties
        self.delta = Vector()
        self.coordinates = Vector()

        #cumulate angle, center of rotation and current drag rotation
        self.angle = 0.0
        self.rotation_center = Vector()
        self.rotation = 0.0

        #flag indicating scenegraph updates are complete
        self.sg_ok = False

        #refrence to scenegrapg root node (used internally)
        self._sg_root = None

        #set to indicate to base tracker not to push updates during on_drag()
        self.override = False

    def update(self, line_start=None, line_end=None):
        """
        Update the drag line and partially-selected nodes
        """

        self._update_drag_line(line_start, line_end)

        if self.partial_coords:
            self._update_partial_nodes()

    def _update_partial_nodes(self):
        """
        Update partially selected drag nodes
        """

        #iterate SoCoordinate3 nodes and update the coordinates at the
        #locations specified by the accompanying indices list
        _coords = []

        #retrieve the coordinates to transform
        for _i, _v in self.partial_coords:

            for _j in self.partial_indices[_i]:
                _coords.append(_v.point.getValues()[_j].getValue())

        #transform coordinates
        _coords = ViewState().transform_points(_coords, self.node_group)
        _k = 0

        #write transformed coordinates back to scenegraph nodes
        for _i, _v in self.partial_coords:

            for _j in self.partial_indices[_i]:

                _v.point.set1Value(_j, _coords[_k])
                _k += 1

    def _update_drag_line(self, line_start, line_end):
        """
        Update the drag line
        """

        if line_start is None:
            line_start = self.start

        if line_end is None:
            line_end = self.coordinates

        _p = [tuple(line_start), tuple(line_end)]

        self.drag_line_coord.point.setValues(0, 2, _p)

    def _build_drag_line(self):
        """
        Build the drag line for drag operations
        """

        _m = coin.SoMarkerSet()

        _l = coin.SoLineSet()
        _l.numVertices.setValue(2)

        _d = coin.SoDrawStyle()
        _d.linePattern = 0x0f0f
        _d.lineWeight = 2

        _c = coin.SoBaseColor()
        _c.rgb = (0.0, 0.0, 1.0)

        _g = coin.SoGroup()
        _g.addChild(_d)
        _g.addChild(_c)
        _g.addChild(self.drag_line_coord)
        _g.addChild(_m)
        _g.addChild(_l)

        self.group.addChild(_g)

    def add_node(self, node):
        """
        Add a node to the drag node group
        """

        if not self.drag_node:
            self.drag_node = node

        drag_group = coin.SoSeparator()

        drag_group.addChild(node)

        self.node_group.addChild(drag_group)

        return drag_group

    def add_partial_node(self, node, indices):
        """
        Add a partially-dragged node to the tree, updating only the
        coordiantes in the passed index.

        node - a group containing the geometry to be rendered.
               must include an SoCoordinate3 node.

        indices - index value(s) of coordiantes in coordiante node to
                  be updated by the drag transform
        """


        if not self.drag_node:
            self.drag_node = node

        _rng = range(0, node.getNumChildren())

        for _i in _rng:

            _n = node.getChild(_i)

            if isinstance(_n, coin.SoCoordinate3):
                self.partial_coords.append(_n)
                break

        self.partial_indices.append(indices)
        self.node.partial_group.addChild(node)


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

        self.reset()

    @staticmethod
    def _insert(drag_state):
        """
        Delayed callback for sg_ok
        """

        drag_state._sg_root.insertChild(drag_state.group, 0)
        drag_state.sg_ok = True

    def insert(self):
        """
        Custom function to manage drag state insertion and provide
        flag when scenegraph has been updated
        """

        self.sg_ok = False

        self._sg_root = ViewState().sg_root
        todo.delay(DragState()._insert, DragState())

    def reset(self):
        """
        State reset function
        """

        self.group.removeAllChildren()

        self.__init__()
