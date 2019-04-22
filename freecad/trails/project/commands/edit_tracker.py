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

def create(coord, object_name, tracker_type):
    """
    Factory method for edit tracker
    """

    coord[2] = C.Z_DEPTH[2]

    nam = 'Tracker' + '_' + tracker_type + '_' \
          + str(hash((coord[0], coord[1], coord[2])))

    #return editTracker(pos=coord, name=nam)
    return EditTracker(coord, object_name, nam, tracker_type)


class EditTracker(Tracker):
    """
    A custom edit tracker
    """

    def __init__(self, pos, object_name, node_name, tracker_type):

        self.pos = pos
        self.name = node_name
        self.tracker_type = tracker_type

        self.inactive = False

        self.color = coin.SoBaseColor()

        self.marker = coin.SoMarkerSet()
        self.set_marker(False)

        self.coords = coin.SoCoordinate3()
        self.coords.point.setValue((pos.x, pos.y, pos.z))

        selnode = None

        if self.inactive:
            selnode = coin.SoSeparator()

        else:
            selnode = coin.SoType.fromName("SoFCSelection").createInstance()
            selnode.documentName.setValue(App.ActiveDocument.Name)
            selnode.objectName.setValue(object_name)
            selnode.subElementName.setValue(node_name)

        node = coin.SoAnnotation()

        selnode.addChild(self.coords)
        selnode.addChild(self.color)
        selnode.addChild(self.marker)

        node.addChild(selnode)

        ontop = not self.inactive

        Tracker.__init__(
            self, children=[node], ontop=ontop, name="EditTracker")

        self.on()

    def set(self, pos):
        """
        Set method
        """
        self.coords.point.setValue((pos.x,pos.y,pos.z))

    def get(self):
        """
        Get method
        """
        _pt = self.coords.point.getValues()[0]
        return App.Vector(_pt)

    def move(self, delta):
        """
        Move method
        """
        self.set(self.get().add(delta))

    def set_style(self, style):
        """
        Set the marker style based on the passed tuple
        """
        self.color.rgb = style[0]

    def set_marker(self, is_open=True):
        """
        Set the marker style to either an open or closed circle
        """

        marker_type = 'CIRCLE'

        if is_open:
            marker_type = 'circle'

        self.marker.markerIndex = Gui.getMarkerIndex(marker_type, 11)
