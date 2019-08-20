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
Customized edit tracker from DraftTrackers.editTracker
"""

from pivy import coin

from FreeCAD import Vector

from ..support.drag_state import DragState
from ..support.view_state import ViewState

from .base_tracker import BaseTracker

class NodeTracker(BaseTracker):
    """
    Tracker object for nodes
    """

    def __init__(self, names, point, nodes=None):
        """
        Constructor
        """

        self.type = 'NODE'

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = [nodes]

        self.is_end_node = False
        self.point = point

        #build node structure for the node tracker
        self.coord = coin.SoCoordinate3()
        self.marker = coin.SoMarkerSet()
        self.drag_point = None

        super().__init__(
            names=names, children=[self.coord, self.marker] + nodes
        )

        self.update()

    def start_drag(self):
        """
        Initialize drag ops
        """

        if not self.is_selected():
            return

        super().start_drag()

        self.drag_point = tuple(self.point)

    def on_drag(self):
        """
        Override of base function
        """

        super().on_drag()

        if not self.drag_point:
            return

        self.drag_point = ViewState().transform_points(
            [self.point], DragState().drag_node)[0]

    def end_drag(self):
        """
        Override of base function
        """

        self.update([self.drag_point])

        super().end_drag()

    def update(self, coord=None):
        """
        Update the coordinate position
        """

        #if we have a list of points, pick the first
        if isinstance(coord, list):
            coord = coord[0]

        if not coord:
            coord = self.point

        _c = coord

        if not isinstance(coord, tuple):
            _c = tuple(_c)

        self.coord.point.setValue(_c[:3])

        self.point = _c

    def get(self):
        """
        Get method
        """

        return Vector(self.coord.point.getValues()[0].getValue())

    def finalize(self, node=None, parent=None):
        """
        Cleanup
        """

        super().finalize(self.node, parent)
