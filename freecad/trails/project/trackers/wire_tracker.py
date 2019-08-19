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
Customized wire tracker from DraftTrackers.wireTracker
"""

from pivy import coin

from ..support.drag_state import DragState
from ..support.mouse_state import MouseState
from ..support.view_state import ViewState

from .base_tracker import BaseTracker

class WireTracker(BaseTracker):
    """
    Customized wire tracker

    self.points - list of Vectors
    self.selction_nodes -
        list of point indices which correspond to node trackers
    """

    def __init__(self, names, nodes=None):
        """
        Constructor
        """

        self.line = coin.SoLineSet()
        self.name = names[2]
        self.coord = coin.SoCoordinate3()
        self.points = None
        self.selection_nodes = None
        self.selection_indices = []

        self.group = coin.SoSeparator()
        self.drag_node = None
        self.drag_coord = None
        self.drag_start = []
        self.drag_points = []
        self.drag_refresh = True
        self.drag_override = False

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = list(nodes)

        nodes += [self.coord, self.line]

        super().__init__(names=names, children=nodes)

    def set_points(self, points=None, nodes=None, indices=None):
        """
        Set the node trackers points

        points - actual points which make up the line
        nodes - references to node trackers
        indices - index of point in self.points that node updates
        """

        if not points:

            if not nodes:
                return

            points = [_v.get() for _v in nodes]

        self.points = points

        _l = 0

        if nodes:
            _l = len(nodes)

        #only two nodes and no indices?  nodes define entire line
        if _l == 2 and not indices:
            indices = [0, len(self.points) - 1]

        self.selection_nodes = nodes
        self.selection_indices = indices

    def get_points(self):
        """
        Return the list of points with node tracker points uupdated
        """

        _points = self.points

        if self.selection_indices:
            _j = 0

            for _i in self.selection_indices:

                if _i is None:
                    continue

                if _i == -1:
                    _i = len(_points) - 1

                _points[_i] = self.selection_nodes[_j].point
                _j += 1

        return _points

    def update(self, points=None):
        """
        Update the wire tracker coordinates based on passed list of
        SoCoordinate3 references
        """

        if not points:
            points = self.points

        if not points:
            return

        _p = points[:]

        if not isinstance(points[0], tuple):
            _p = [tuple(_v) for _v in _p]

        self.coord.point.setValues(0, len(points), _p)
        self.line.numVertices.setValue(len(points))

        self.points = _p

        super().refresh()

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        if MouseState().button1.state == 'UP':
            return

        _sel = []

        if self.selection_nodes:
            _sel = [_v.state.selected.value for _v in self.selection_nodes]

        self.state.selected.ignore = False
        self.state.selected.value = False

        if _sel and (all(_sel) or any(_sel)):
            self.state.selected.value = True
            self.state.selected.ignore = True

        super().button_event(arg)

    def before_drag(self):
        """
        Override base fucntion
        """

        if not self.state.selected.value:
            return

        super().before_drag()

    def start_drag(self):
        """
        Override of base function
        """

        if not self.state.draggable:
            return

        #base implementation if no selection nodes
        if self.selection_nodes is None:
            super().start_drag()
            return

        _states = [_v.state.selected.value for _v in self.selection_nodes]

        #base implementation if all nodes selected
        if all(_states):
            super().start_drag()
            return

        #custom implementation for partial selection
        self.state.dragging = not all(_states) and any(_states)

        if not self.state.dragging:
            return

        _drag_indices = [
            _i for _i, _v in enumerate(self.selection_nodes)\
                if _v.state.dragging
        ]

        self.drag_node = self.copy()

        DragState().add_partial_node(self.drag_node, _drag_indices)

    def on_drag(self):
        """
        Override of base function
        """

        if self.drag_override:
            return

        #abort unselected / non-partial drag
        if not self.state.dragging:
            return

        if not self.state.selected.value:
            return

        super().on_drag()

    def _partial_drag(self):
        """
        Perform partial drag if ok
        """

        if not DragState().sg_ok:
            return

        self.drag_points = []

        for _v in self.selection_nodes:

            if _v.state.dragging:
                self.drag_points.append(_v.drag_point)
            else:
                self.drag_points.append(_v.point)

        #if self.drag_refresh:
           # self.refresh_drag()

    def end_drag(self):
        """
        Override of base function
        """

        #pull the updated tuples from the drag node
        _values = []
        _node = self.drag_node

        if not _node:
            _node = self.drag_group.getChild(0)

        _values = [_v.getValue() for _v in _node.getChild(3).point.getValues()]

        if _values:
            self.update(_values)

        _coords = ViewState().transform_points(_values, DragState().drag_node)

        self.update(_coords)
        self.drag_node = None
        self.drag_group = None

        super().end_drag()

    def finalize(self, node=None, parent=None):
        """
        Cleanup
        """

        if node is None:
            node = self.switch

        super().finalize(node, parent)
