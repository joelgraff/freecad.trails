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
    return EditTracker(coord, object_name, nam)


class EditTracker(Tracker):
    """
    A custom edit tracker
    """

    def __init__(self, pos, node_name, nodes=None, style=None):

        self.position = pos
        self.name = node_name

        self.inactive = False

        self.color = coin.SoBaseColor()

        self.marker = coin.SoMarkerSet()

        self.coords = coin.SoCoordinate3()
        self.coords.point.setValue((pos.x, pos.y, pos.z))
        node = coin.SoSeparator()

        #add child nodes to the selection node
        for _node in [self.coords, self.color, self.marker]:
            node.addChild(_node)

        child_nodes = nodes

        if not isinstance(nodes, list):
            child_nodes = [nodes]

        child_nodes += [node]

        ontop = not self.inactive

        Tracker.__init__(
            self, children=child_nodes, ontop=ontop, name="EditTracker")

        if style:
            self.set_style(style)

        self.on()

    def set(self, pos):
        """
        Set method
        """
        self.position = pos
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

        self.marker.markerIndex = \
            Gui.getMarkerIndex(style['shape'], style['size'])

        self.color.rgb = style['color']
