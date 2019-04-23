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

import FreeCAD as App
import FreeCADGui as Gui

from DraftTrackers import Tracker

from ..support.utils import Constants as C

def create(points):
    """
    Factory method for edit tracker
    """

    for point in points:
        point[2] = C.Z_DEPTH[2]

    return DragTracker(points)


class DragTracker(Tracker):
    """
    Customized wire tracker
    """

    def __init__(self, points):
        """
        Constructor
        """

        self.line = coin.SoLineSet()
        self.line.numVertices.setValue(len(points))

        self.coords = coin.SoCoordinate3()

        self.transform = coin.SoTransform()

        self.update(points)

        Tracker.__init__(
            self, children=[self.coords, self.line, self.transform], name="DragTracker"
        )

        self.node = self.switch.getChild(0)
        self.draw_style = self.node.getChild(0)
        self.color = self.node.getChild(1)

        self.color.rgb = (0.0, 0.0, 0.0)

        self.on()

    def update(self, points):
        """
        Update
        """

        if not points:
            return

        self.line.numVertices.setValue(len(points))

        for _i, _pt in enumerate(points):
            self.coords.point.set1Value(_i, list(_pt))

    def set_placement(self, placement):
        """
        Transform the tracker by the passed placement
        """

        vec = placement.Base
        vec_str = str(vec.x) + ' ' + str(vec.y) + ' ' + str(vec.z)
        self.transform.center.setValue(tuple([10000, 10000, 0]))
        self.transform.translation.setValue(tuple(vec))

    def set_style(self, style):
        """
        Set the ViewObject style based on the passed tuple.
        """

        pass
