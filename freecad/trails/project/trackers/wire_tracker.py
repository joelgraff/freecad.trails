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

from .base_tracker import BaseTracker

from ..support.drag_state import DragState

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
        self.drag_coord = None
        self.drag_idx = None
        self.drag_start = []

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = list(nodes)

        nodes += [self.coord, self.line]

        super().__init__(names=names, children=nodes)

    def set_points(self, points, nodes, indices=None):
        """
        Set the node trackers points

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

        #more than two nodes and index mismatch = error
        if _l > 2:

            if not indices or len(indices) != _l:

                print('WireTracker', self.name, 'node mismatch')
                return

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
                _points[_i] = self.selection_nodes[_j].point
                _j += 1

        return _points

    def update(self, points=None):
        """
        Update the wire tracker coordinates based on passed list of
        SoCoordinate3 references
        """

        if not points:
            points = self.get_points()

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

        _sel = []

        if self.selection_nodes:
            _sel = [_v.state.selected.value for _v in self.selection_nodes]

        self.state.selected.ignore = False

        if not all(_sel) and any(_sel):
            self.state.selected.value = True
            self.state.selected.ignore = True

        super().button_event(arg)

    def start_drag(self):
        """
        Override of base function
        """

        if self.selection_nodes is None:
            super().start_drag()
            return

        _states = [_v.state.selected.value for _v in self.selection_nodes]

        self.state.dragging = not all(_states) and any(_states)

        if not self.state.dragging:
            return

        self.drag_idx = [_i for _i, _v in enumerate(_states) if _v][0]

        _node = self.copy(self.node)

        self.group.addChild(_node)
        self.drag_coord = _node.getChild(3)
        self.drag_start = self.points[:]

        self.insert_node(self.group, 0)

    def on_drag(self):
        """
        Override of base function
        """

        #abort unselected
        if not self.state.dragging:
            return

        #partially-selected wires will have a drag_idx.
        #fully-selected / unselected will not
        if self.drag_idx is not None:

            if DragState().sg_ok:
                self._partial_drag()

            return

        super().on_drag()

    def _partial_drag(self):
        """
        Perform partial drag if ok
        """

        if not DragState().sg_ok:
            return

        #refresh the matrix only if invalid, since all wires will want the
        #same transformation
        self.points[self.drag_idx] =\
             self.transform_points(
                 [self.drag_start[self.drag_idx]],
                 DragState().drag_node,
                 refresh=True
             )[0]

        self.drag_coord.point.setValues(0, len(self.points), self.points)

    def end_drag(self):
        """
        Override of base function
        """

        _node = None

        if DragState().node:
            _node = DragState().node_group.getChild(0)

        #transform all points which are not nodes
        _points = []

        if self.selection_indices:

            for _i, _v in enumerate(self.points):
                if _i not in self.selection_indices:
                    _points.append(_v)

        else:
            _points = self.points

        _points = self.transform_points(_points, _node, refresh=True)

        self.update(_points)

        self.drag_idx = None
        self.drag_coord = None
        self.drag_start = []
        self.remove_node(self.group)
        self.group.removeAllChildren()

        super().end_drag()

    def finalize(self, node=None, parent=None):
        """
        Cleanup
        """

        if node is None:
            node = self.switch

        super().finalize(node, parent)
