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

import math

from pivy import coin

from FreeCAD import Vector

from DraftGui import todo

from .singleton import Singleton
from .view_state import ViewState

from ..support.utils import Constants as C
from ...geometry import support

class DragState(metaclass=Singleton):
    """
    Class to track the current state of the active or specified view
    """

    def __init__(self):

        self.start = Vector()

        self.root = coin.SoSeparator()
        self.node_group = coin.SoSeparator()
        self.partial_group = coin.SoSeparator()

        self.partial_nodes = []
        self.partial_coords = []
        self.partial_indices = []

        self.node_translate = coin.SoTransform()
        self.node_rotate = coin.SoTransform()
        self.drag_node = None

        self.drag_line_coord = coin.SoCoordinate3()

        self._build_drag_line()

        self.root.addChild(self.partial_group)
        self.root.addChild(self.node_translate)
        self.root.addChild(self.node_rotate)
        self.root.addChild(self.node_group)

        self.abort = False

        #coordinate tracking properties
        self.delta = Vector()
        self.coordinates = Vector()

        #cumulate angle, center of rotation and current drag rotation
        self.angle = 0.0
        self.rotation_center = None
        self.rotation = 0.0

        #flag indicating scenegraph updates are complete
        self.sg_ok = False

        #reference to scenegrapg root node (used internally)
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

        #transform coordinates
        _coords = ViewState().transform_points(self.partial_coords, self.node_group)
        _k = 0

        #write transformed coordinates back to scenegraph nodes
        for _i, _v in enumerate(self.partial_nodes):

            for _j in self.partial_indices[_i]:

                _v.point.set1Value(_j, _coords[_k][:3])
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

        self.root.addChild(_g)

    def add_node(self, node):
        """
        Add a node to the drag node group
        """

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

        indices - index value(s) of coordinates in node to
                  be updated by the drag transform
        """

        _rng = range(0, node.getNumChildren())

        for _i in _rng:

            _n = node.getChild(_i)

            if isinstance(_n, coin.SoCoordinate3):

                self.partial_nodes.append(_n)

                _coords = _n.point.getValues()

                for _i in indices:
                    self.partial_coords.append(_coords[_i])

                break

        _drag_group = coin.SoSeparator()
        _drag_group.addChild(node)

        self.partial_indices.append(indices)
        self.partial_group.addChild(_drag_group)

        return _drag_group

    def finish(self):
        """
        Return the transformation matrix for the provided node
        """

        #node was never added, but drag state members may have changed
        if not self.root or not self._sg_root:
            self.reset()
            return

        self.sg_ok = False

        todo.delay(DragState()._remove, DragState())

    @staticmethod
    def _remove(drag_state):
        """
        Delayed callback for sg_ok
        """

        if drag_state._sg_root:
            drag_state._sg_root.removeChild(drag_state.root)

        drag_state.sg_ok = True
        drag_state.reset()

    @staticmethod
    def _insert(drag_state):
        """
        Delayed callback for sg_ok
        """

        drag_state._sg_root.insertChild(drag_state.root, 0)
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

        self.root.removeAllChildren()

        self.__init__()

##########################
## Transformation routines
##########################

    def translate(self, coord, micro_drag=False):
        """
        Manage drag geometry translation
        """

        #accumulate the movement from the previous mouse position
        _delta = coord.sub(self.coordinates)

        self.delta = Vector(self.node_translate.translation.getValue())
        _scale = 1.0

        if micro_drag:
            _scale = 0.10

        self.delta = self.delta.add(_delta.multiply(_scale))

        self.node_translate.translation.setValue(tuple(self.delta))


    def rotate(self, coord, micro_drag=False):
        """
        Manage rotation during dragging
        coord - coordinates for the rotation update
        """

        _angle = 0.0

        if self.rotation_center:
            _angle = support.get_bearing(coord.sub(self.rotation_center))

        else:

            _dx_vec = coord.sub(
                Vector(self.node_translate.translation.getValue())
            )

            self.node_rotate.center.setValue(coin.SbVec3f(tuple(_dx_vec)))

            self.rotation_center = coord
            self.rotation = 0.0
            self.angle = 0.0

        _scale = 1.0

        if micro_drag:
            _scale = 0.10

        _delta = self.angle - _angle

        if _delta < -math.pi:
            _delta += C.TWO_PI

        elif _delta > math.pi:
            _delta -= C.TWO_PI

        self.rotation += _delta * _scale
        self.angle = _angle

        #update the +z axis rotation for the transformation
        self.node_rotate.rotation =\
            coin.SbRotation(coin.SbVec3f(0.0, 0.0, 1.0), self.rotation)
