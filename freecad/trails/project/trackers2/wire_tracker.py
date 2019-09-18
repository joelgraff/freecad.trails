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

from ..support.publisher import PublisherEvents as Events

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

        if nodes and not isinstance(nodes, list):
            nodes = [nodes]

        if not points:

            if not nodes:
                return

            points = [_v.get() for _v in nodes]
            indices = list(range(0, len(points)))

        self.points = points

        _l = 0

        if nodes:
            _l = len(nodes)

        #only two nodes and no indices?  nodes define entire line
        if _l == 2 and not indices:
            indices = [0, len(self.points) - 1]

        #register the wire tracker as a subscriber to node updates
        if nodes:
            for _n in nodes:
                _n.register(self, Events.NODE.UPDATED)

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

    def notify(self, event, message):
        """
        Override base implementation
        """

        super().notify(event, message, True)

        if event != Events.NODE.UPDATED:
            return

        _sel = []

        #must be selected unless it's controlled by selection nodes
        if not self.selection_nodes:

            if not self.is_selected():
                return

        else:

            #get a list of the indices of points that correlate to
            #actively-selected selection nodes
            for _i, _v in enumerate(self.selection_nodes):

                if _v.is_selected():
                    _sel.append(self.selection_indices[_i])

            if not _sel:
                return

        #if fewer nodes are selected than there are wire points, the
        #wire is not enitrely selected
        if len(_sel) != len(self.points):
            SelectState().partial_select(self)
            self.partial_idx = _sel

        self.update()

    def update(self, points=None):
        """
        Update the wire tracker coordinates based on passed list of
        SoCoordinate3 references
        """

        _p = None

        if points:
            _p = points[:]

        elif self.points:
            _p = self.points[:]

        if not _p:
            return

        if not isinstance(_p[0], tuple):
            _p = [tuple(_v) for _v in _p]

        if self.selection_nodes:

            for _i, _j in enumerate(self.selection_indices):
                _p[_j] = tuple(self.selection_nodes[_i].get())

        self.coord.point.setValues(0, len(_p), _p)
        self.line.numVertices.setValue(len(_p))

        self.points = _p

        super().refresh()

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        super().button_event(arg)

        #if MouseState().button1.state == 'DOWN':
            #self.validate_selection()

        self.refresh()

    def validate_selection(self):
        """
        Validate the wire's selection state against the selected nodes
        """

        #no validation for manual selection
        if self.is_selected() == 'MANUAL':
            return

        _sel = []
        _sel_state = self.is_selected()

        #create truth list of node selection states
        if self.selection_nodes:
            _sel = [_v.is_selected() != '' for _v in self.selection_nodes]

        #if not all nodes are selected, but the wire is, and the
        #wire was clicked, select all nodes
        if not all(_sel) and _sel_state == 'FULL'\
            and self.name in MouseState().component:

            for _v in self.selection_nodes:
                if _v.is_selected() != 'FULL':
                    SelectState().select(_v, force=True)

        #all nodes selected, but wire is not full
        elif _sel and all(_sel) and _sel_state != 'FULL':
            SelectState().select(self, force=True)

        #any (but not all) node selected, and wire is not partial
        elif any(_sel) and _sel_state != 'PARTIAL':
            SelectState().partial_select(self)

        #no nodes selected, but wire is selected
        elif _sel and not any(_sel) and _sel_state:
            SelectState().deselect(self)

    def start_drag(self):
        """
        Override of base function
        """

        #if the wire is not specifically selected, abort.
        #Indirect selection / dragging via selection nodes is handled
        #vis pub/sub signaling
        if self.selected != 'FULL':
            return

        super().start_drag()

    def end_drag(self):
        """
        Override of base function
        """

        _node = None

        if not self.drag_copy:
            return

        #pull the updated tuples from the drag node
        for _n in self.drag_copy.getChildren():

            if isinstance(_n, coin.SoCoordinate3):
                _node = _n.point
                break

        if _node and not DragState().abort:

            _coords = [_v.getValue() for _v in _node.getValues()]

            #nodes and partially selected lines do not need
            #a final transformation
            if SelectState().is_selected(self) == 'FULL':

                _coords = ViewState().transform_points(
                    _coords, DragState().node_group)

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
