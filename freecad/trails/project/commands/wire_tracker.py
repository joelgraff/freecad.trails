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

from DraftTrackers import Tracker

from .edit_tracker import EditTracker
from ..support.utils import Constants as C

def create(object_name, points):
    """
    Factory method for edit tracker
    """

    for point in points:
        point[2] = C.Z_DEPTH[2]

    return WireTracker(object_name, points)


class WireTracker(Tracker):
    """
    Customized wire tracker
    """

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

        self.doc = doc
        self.edit_trackers = []
        self.object_name = object_name

        self.line = coin.SoLineSet()
        self.line.numVertices.setValue(len(points))

        self.coords = coin.SoCoordinate3()
        self.transform = coin.SoTransform()
        self.transform.translation.setValue([0.0, 0.0, 0.0])

        self.update(points=points)

        Tracker.__init__(
            self, False, None, None, [self.transform, self.coords, self.line], name="WireTracker"
        )

        self.node = self.switch.getChild(0)
        self.draw_style = self.node.getChild(0)

        self.color = self.node.getChild(1)
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
        Clears and rebuilds the wire and edit trackers
        """

        self.line.numVertices.setValue(len(points))

        self.finalize_edit_trackers()

        for _i, _pt in enumerate(points):

            _pt.z = C.Z_DEPTH[2]

            _et = EditTracker(
                self.doc, self.object_name, 'Node' + str(_i), self.transform
            )

            _et.set_style(self.style[0])
            _et.update(_pt)

            self.edit_trackers.append(_et)

    def update_placement(self, placement):
        """
        Updates the placement for the wire and the trackers
        """

        return

    def finalize_edit_trackers(self):
        """
        Destroy existing editr trackers
        """

        if not self.edit_trackers:
            return

        for _et in self.edit_trackers:
            _et.finalize()

        self.edit_trackers.clear()

    def finalize(self):
        """
        Override of the parent method
        """

        self.finalize_edit_trackers()
        super().finalize()
