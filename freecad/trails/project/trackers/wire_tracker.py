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

from ..support.const import Const
from .base_tracker import BaseTracker


class WireTracker(BaseTracker):
    """
    Customized wire tracker
    """


    class STYLE(Const):
        """
        Const Style class
        """

        DEFAULT = {
            'line width': None,
            'line style': coin.SoDrawStyle.LINES,
            'line weight': 3,
            'line pattern': None,
            'select': True
        }

        EDIT = {
            'line width': None,
            'line style': coin.SoDrawStyle.LINES,
            'line weight': 3,
            'line pattern': 0x0f0f, #oxaaa
            'select': False
        }

    def __init__(self, names, nodes=None, style=STYLE.DEFAULT):
        """
        Constructor
        """

        self.line = coin.SoLineSet()
        self.coords = coin.SoCoordinate3()

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = [nodes]

        nodes += [self.coords, self.line]

        print('\n\t-->style', style)
        super().__init__(names=names, children=nodes, select=style['select'])

        self.switch = coin.SoSwitch() # this is the on/off switch

        if names[2]:
            self.switch.setName(names[2])

        self.switch.addChild(self.node)

        self.on()

    def on(self):
        self.switch.whichChild = 0
        self.visible = True

    def off(self):
        self.switch.whichChild = -1
        self.visible = False

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

        for _i, _pt in enumerate(points):
            self.coords.point.set1Value(_i, list(_pt))

    def update_placement(self, placement):
        """
        Updates the placement for the wire and the trackers
        """

        return

    def set_style(self, style):
        """
        Update the tracker style
        """

        if style['line width']:
            self.draw_style.lineWidth = style['line width']

        self.draw_style.style = style['line style']
        self.draw_style.lineWeight = style['line weight']

        if style['line pattern']:
            self.draw_style.linePattern = style['line pattern']

    def finalize(self):
        """
        Cleanup
        """

        self._removeSwitch(self.switch)
