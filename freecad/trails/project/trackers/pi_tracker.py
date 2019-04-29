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

class PiTracker(BaseTracker):
    """
    Tracker class which manages alignment PI  and tangnet
    picking and editing
    """
    style = {
        'default node':
        {
            'shape': 'CIRCLE_FILLED',
            'size': 9,
            'color': (0.8, 0.8, 0.8)
        },

        'default wire':
        {
            'line width': None,
            'line style': coin.SoDrawStyle.LINES,
            'line weight': 3,
            'line pattern': None
        },

        'edit node':
        {
            'shape': 'CIRCLE_LINE',
            'size': 9,
            'color': (0.8, 0.4, 0.4)
        },

        'edit wire':
        {
            'line width': None,
            'line style': coin.SoDrawStyle.LINES,
            'line weight': 3,
            'line pattern': 0x0f0f #oxaaa
        }
    }

    def __init__(self, doc, object_name, points):
        """
        Constructor
        """

        self.node_trackers = []
        self.wire_trackers = []

        self.transform = coin.SoTransform()
        self.transform.translation.setValue([0.0, 0.0, 0.0])

        print('\ntracker points ', points)

        self.update(points=points)

        child_nodes = \
            self.node_trackers + self.wire_trackers + [self.transform]

        super().__init__(doc=doc, object_name=object_name,
                         node_name='PI_Tracker', nodes=child_nodes)

        self.color.rgb = (0.0, 0.0, 1.0)
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
        Clears and rebuilds the wire and node trackers
        """

        self.line.numVertices.setValue(len(points))

        self.finalize_trackers()

        prev_coord = None

        for _i, _pt in enumerate(points):

            #set z value on top
            _pt.z = C.Z_DEPTH[2]

            #build edit trackers
            _nt = NodeTracker(self.doc, self.object_name, 'NODE_' + str(_i),                     _pt, self.transform
            )

            _nt.set_style(self.style['default node'])
            _nt.update(_pt)

            self.node_trackers.append(_nt)

            if not prev_coord is None:

                points = [prev_coord, _pt]

                _wt = WireTracker(
                    self.doc, self.object_name, points, self.transform
                )

                _wt.set_style(self.style['default wire'])

                self.wire_trackers.append(_wt)

            prev_coord = _pt

    def update_placement(self, vector):
        """
        Updates the placement for the wire and the trackers
        """

        print('\n<<<--- setting transofrm ', list(vector))
        self.transform.translation.setValue(list(vector))

    def finalize_trackers(self, tracker_list=None):
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

        self.finalize_trackers()
        super().finalize()
