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
Drag tracker class
"""

import math

from pivy import coin

from DraftGui import todo

from ...support.singleton import Singleton
from ...support.utils import Constants as C
from ....geometry import support

from .view_state import ViewState
from .smart_tuple import SmartTuple

from .base import Base

class DragState(Base, metaclass=Singleton):
    """
    Class to track the current state of the active or specified view
    """

    def __init__(self):

        super().init(name='Drag Tracker')

        self.start = ()

        self.drag_switch = coin.SoSwitch()
        self.drag_node = coin.SoSeparator()
        self.drag_event_callback = coin.SoEventCallback()
        self.full_group = coin.SoSeparator()
        self.manual_group = coin.SoSeparator()

        self.drag_transform = coin.SoTransform()
        self.drag_tracker_node = None
        self.drag_point = None

        self.update_translate = True
        self.update_rotate = True

        self.drag_line_coord = coin.SoCoordinate3()

        self.drag_event_callback.setPath(None)

        self.drag_node.addChild(self.drag_event_callback)
        self.drag_node.addChild(self.manual_group)
        self.drag_node.addChild(self.drag_transform)
        self.drag_node.addChild(self.full_group)

        self.drag_switch.addChild(self._build_drag_line())
        self.drag_switch.addChild(self.drag_node)
        self.drag_switch.whichChild = -3

        self.abort = False

        #coordinate tracking properties
        self.delta = ()
        self.coordinates = ()

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

        #current drag point is set to the end of the drag line by default
        self.drag_point = _p[1]

    def _build_drag_line(self):
        """
        Build the drag line for drag operations
        """
        #pylint: disable=no-member
        _l = coin.SoLineSet()
        _l.numVertices.setValue(2)

        _d = coin.SoDrawStyle()
        _d.linePattern = 0x0f0f
        _d.lineWeight = 2

        _c = coin.SoBaseColor()
        _c.rgb = (0.8, 0.8, 1.0)

        _g = coin.SoGroup()
        _g.addChild(_d)
        _g.addChild(_c)
        _g.addChild(self.drag_line_coord)
        _g.addChild(coin.SoMarkerSet())
        _g.addChild(_l)

        return _g

    def add_manual_node(self, node):
        """
        Add a node to the drag state that is updated manually
        If parent is none, creates a new manual group with rotation and
        translation transforms.  Otherwise, appends to existing.
        """

        _drag_group = coin.SoSeparator()
        _drag_group.addChild(coin.SoTransform())
        _drag_group.addChild(node)

        self.manual_group.addChild(_drag_group)

        return _drag_group

    def add_node(self, node):
        """
        Add a node to the drag node group
        """

        drag_group = coin.SoSeparator()
        drag_group.addChild(node)

        self.drag_node.addChild(drag_group)

        return drag_group

    def finish(self):
        """
        Return the transformation matrix for the provided node
        """

        #node was never added, but drag state members may have changed
        if not self._sg_root:
            self.reset()
            return

        self.sg_ok = False

        todo.delay(DragState()._remove, DragState())

    def reset(self):
        """
        State reset function
        """

        self.drag_switch.removeAllChildren()

        self.__init__()

##########################
## Transformation routines
##########################

    def translate(self, coord):
        """
        Manage drag geometry translation
        """

        if not self.update_translate:
            return

        #accumulate the movement from the previous mouse position
        _delta = SmartTuple._sub(coord, self.coordinates)

        self.delta = SmartTuple._add(
            self.drag_transform.translation.getValue(), _delta)

        self.drag_transform.translation.setValue(self.delta)

    def rotate(self, coord):
        """
        Manage rotation during dragging
        coord - coordinates for the rotation update
        """

        if not self.update_rotate:
            return

        _angle = 0.0

        if self.rotation_center:
            _angle = support.get_bearing(
                SmartTuple._sub(coord, self.rotation_center))

        else:

            _dx_vec = SmartTuple._sub(
                coord, self.drag_transform.translation.getValue())

            self.drag_transform.center.setValue(coin.SbVec3f(_dx_vec))

            self.rotation_center = coord
            self.rotation = 0.0
            self.angle = 0.0


        _delta = self.angle - _angle

        if _delta < -math.pi:
            _delta += C.TWO_PI

        elif _delta > math.pi:
            _delta -= C.TWO_PI

        self.rotation += _delta
        self.angle = _angle

        #update the +z axis rotation for the transformation
        self.drag_transform.rotation =\
            coin.SbRotation(coin.SbVec3f(0.0, 0.0, 1.0), self.rotation)
