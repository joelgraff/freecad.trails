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

from DraftTrackers import Tracker

from ..support.utils import Constants as C

def create(coord, tracker_type):
    """
    Factory method for edit tracker
    """

    coord[2] = C.Z_DEPTH[2]

    nam = 'Tracker' + '_' + tracker_type + '_' \
          + str(hash((coord[0], coord[1], coord[2])))

    print('tracker ', nam)
    _et = EditTracker(coord, nam, tracker_type)
    _et.raiseTracker()
    _et.on()

    return _et

class EditTracker(Tracker):
    """
    A custom edit tracker
    """

    def __init__(self, pos=App.Vector(0, 0, 0), name="None", inactive=False,
                 tracker_type=None):

        self.pos = pos
        self.name = name
        self.tracker_type = tracker_type

        #until here
        self.color = coin.SoBaseColor()
        self.marker = coin.SoMarkerSet() # this is the marker symbol
        self.marker.markerIndex = Gui.getMarkerIndex("circle", 9)
        self.coords = coin.SoCoordinate3() # this is the coordinate
        self.coords.point.setValue((pos.x, pos.y, pos.z))

        selnode = None

        if inactive:
            selnode = coin.SoSeparator()

        else:
            selnode = coin.SoType.fromName("SoFCSelection").createInstance()
            selnode.documentName.setValue(App.ActiveDocument.Name)
            selnode.objectName.setValue(name)
            selnode.subElementName.setValue(name)

        node = coin.SoAnnotation()

        selnode.addChild(self.coords)
        selnode.addChild(self.color)
        selnode.addChild(self.marker)

        node.addChild(selnode)

        ontop = not inactive

        Tracker.__init__(
            self, children=[node], ontop=ontop, name="EditTracker")

        self.on()

    #def updateListIdx(self,listIdx):
        #selnode.subElementName.setValue("EditNode"+str(listIdx))

    def set(self, pos):
        self.coords.point.setValue((pos.x,pos.y,pos.z))

    def get(self):
        p = self.coords.point.getValues()[0]
        return App.Vector(p[0],p[1],p[2])

    def move(self, delta):
        self.set(self.get().add(delta))
