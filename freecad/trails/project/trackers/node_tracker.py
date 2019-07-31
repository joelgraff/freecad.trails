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

        super().__init__(
            names=names, children=[self.coord, self.marker] + nodes
        )

        self.update()

    def end_drag(self):
        """
        Override of base function
        """

        super().end_drag()

        _point = self.transform_nodes([self.point])

        self.update(_point)

    def update(self, coord=None):
        """
        Update the coordinate position
        """

        if not coord:
            coord = self.point

        #if we have a list of points, pick the first
        if isinstance(coord, list):
            coord = coord[0]

        _c = coord

        if not isinstance(coord, tuple):
            _c = tuple(_c)

        self.coord.point.setValue(_c)

        self.point = _c

        #update style / state changes
        super().refresh()

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
