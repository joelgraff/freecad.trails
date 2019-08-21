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
from ..support.select_state import SelectState

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

        super().button_event(arg)

    def start_drag(self):
        """
        Override of base function
        """

        _parents = None

        #must be selected unless it's controlled by selection nodes
        if not self.selection_nodes:

            if not self.is_selected():
                return

        else:

            #adjust wire selection state based on existing selection nodes
            _sel = [
                _i for _i, _v in enumerate(self.selection_nodes)\
                if _v.is_selected()
            ]

            if not _sel:
                return

            #self.state.selected.ignore = _sel

            #fully selected node defaults to base start_drag
            if len(_sel) == len(self.selection_nodes):
                super().start_drag()
                return

            #otherwise, partially-select the node...
            for _i in _sel:
                SelectState().partial_select(self.selection_nodes[_i], self)

            self.refresh()

        super().start_drag(_sel)

    def on_drag(self):
        """
        Override of base function
        """

        super().on_drag()

        return

        if self.drag_override:
            return

        #abort unselected / non-partial drag
        if not self.state.dragging:
            return

        if not self.is_selected():
            return

        super().on_drag()

    def end_drag(self):
        """
        Override of base function
        """

        #pull the updated tuples from the drag node
        _values = []
        _node = None

        for _n in self.drag_group.getChild(0).getChildren():

            if isinstance(_n, coin.SoCoordinate3):
                _node = _n.point
                break

        if _node:

            _coords = [_v.getValue() for _v in _node.getValues()]
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
