# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************
"""
Tracker for alignment drafting
"""

import Part

import FreeCAD as App
import FreeCADGUI as Gui

from DraftTrackers import Tracker
from pivy import coin

class AlignmentTracker(Tracker):
    """
    Tracker class for alignment design
    """

    def __init__(self,dotted=False,scolor=None,swidth=None,points = []):

        self.wire = None
        self.points = points
        self.trans = coin.SoTransform()
        self.sep = coin.SoSeparator()
        self.recompute()

        Tracker.__init__(self, dotted, scolor, swidth,
                         [self.trans, self.sep], name="AlignmentTracker")

    def update(self, points):
        self.points = points
        self.recompute()

    def recompute(self):

        if len(self.points) <= 1:
            return

        if self.wire:
            self.sep.removeChild(self.wire)

        c = Part.makeWire(self.points)
  
        c = c.toShape()

        buf = c.writeInventor(2, 0.01)

        try:
            ivin = coin.SoInput()
            ivin.setBuffer(buf)
            ivob = coin.SoDB.readAll(ivin)

        except:

            import re

            buf = buf.replace('\n', '')
            pts = re.findall('point \[(.*?)\]', buf)[0]
            pts = pts.split(',')
            pc = []

            for p in pts:
                v = p.strip().split()
                pc.append([float(v[0]), float(v[1]), float(v[2])])

            coords = coin.SoCoordinate3()
            coords.point.setValues(0, len(pc, pc))

            line = coin.SoLineSet()
            line.numVertices.setValue(-1)

            self.wire = coin.SoSeparator()
            self.wire.addChild(coords)

            self.sep.addChild(self.wire)

        else:
            if ivob and ivob.getNumChildren() > 1:

                self.wire = ivob.getChild(1).getChild(0)
                self.wire.removeChild(self.wire.getChild(0))
                self.wire.removeChild(self.wire.getChild(0))
                self.sep.addChild(self.wire)

            else:
                App.Console.PrintWarning(
                    'AlignmentTracker.recompute() failed to read Inventor string\n'
                )
