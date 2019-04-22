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

import FreeCAD as App
import FreeCADGui as Gui

from DraftTrackers import Tracker, editTracker

from ..support.utils import Constants as C

class WireTracker(Tracker):
    """
    Customized wire tracker
    """

    def __init__(self, wire):
        """
        Constructor
        """

        self.line = coin.SoLineSet()
        self.line.numVertices.setValue(len(wire.Vertexes))

        self.coords = coin.SoCoordinate3()

        self.update(wire)

        Tracker.__init__(
            self, children=[self.coords, self.line], name="WireTracker"
        )

        self.node = self.switch.getChild(0)

        self.draw_style = self.node.getChild(0)
        self.color = self.node.getChild(1)

        self.color.rgb = (0.0, 0.0, 0.0)

        self.on()

    def update(self, wire, forceclosed=False):
        """
        Update
        """

        print ('in update.  wire is none? ', wire is None)
        if wire is None:
            return

        print('vtx count = ', len(wire.Vertexes))
        self.line.numVertices.setValue(len(wire.Vertexes))

        for _i, _pt in enumerate(wire.Vertexes):
            _vec = _pt.Point
            print('wire coord ', _vec)
            self.coords.point.set1Value(_i, [_vec.x, _vec.y, _vec.z])

    def set_style(self, style):
        """
        Set the ViewObject style based on the passed tuple.
        """

