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
Customized wire tracker for PI alignments
"""

from pivy import coin

import FreeCAD as App
import FreeCADGui as Gui

from .base_tracker import BaseTracker
from .node_tracker import NodeTracker
from .wire_tracker import WireTracker

from ..support.utils import Constants as C

class PI_Tracker(BaseTracker):

    style = [ \
        #default
        { \
            'shape': 'CIRCLE_FILLED',
            'size': 9,
            'color': (0.8, 0.8, 0.8)
        },

        #moving
        { \
            'shape': 'CIRCLE_LINE',
            'size': 9,
            'color': (0.8, 0.4, 0.4)
        }
    ]

    def __init__(self, doc, object_name, points):
        """
        Constructor
        """

        self.node_trackers = []
        self.wire_trackers = []

        self.line = coin.SoLineSet()
        self.line.numVertices.setValue(len(points))

        super().__init__(doc=doc, object_name=object_name,
                         node_name='PI_Tracker')

        self.color.rgb = (0.0, 0.0, 1.0)
        self.update(points=points)
        self.on()

    def update(self, points=None, placement=None):
        """
        Update
        """

        if points:
            self.update_points(points)

        if placement:
            self.update_placement(placement)

    def update_points(self, points):
        """
        Clears and rebuilds the wire and edit trackers
        """

        self.line.numVertices.setValue(len(points))

        self.finalize_node_trackers()

        for _i, _pt in enumerate(points):

            #set z value on top
            _pt.z = C.Z_DEPTH[2]

            #build edit trackers
            _nt = NodeTracker(
                self.object_name, 'NODE_' + str(_i), self.transform
            )

            _nt.set_style(self.style[0])
            _nt.update(_pt)

            self.node_trackers.append(_nt)

            #add coordinate to wire
            self.coords.point.set1Value(_i, list(_pt))

    def update_placement(self, placement):
        """
        Updates the placement for the wire and the trackers
        """

        return

    def finalize__trackers(self):
        """
        Destroy existing trackers
        """

        if self.node_trackers:

            for _tracker in self.node_trackers:
                _tracker.finalize()

            self.node_trackers.clear()

        if self.wire_trackers:

            for _tracker in self.wire_trackers:
                _tracker.finalize()

            self.wire_trackers.clear()

    def finalize(self):
        """
        Override of the parent method
        """

        self.finalize_edit_trackers()
        super().finalize()
