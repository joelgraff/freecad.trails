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

import FreeCAD as App
import FreeCADGui as Gui

from DraftTrackers import Tracker

from ..support.utils import Constants as C


class NodeTracker(Tracker):
    """
    A custom edit tracker
    """

    def __init__(self, object_name, node_name, coord, nodes=None):

        super().__init__(object_name, node_name, nodes)

        self.update(coord)
        self.on()

    def update(self, coord):
        """
        Update the coordinate position
        """
        self.coords.point.setValue(tuple(coord))

    def get(self):
        """
        Get method
        """
        _pt = self.coords.point.getValues()[0]

        return App.Vector(_pt)

    def set_style(self, style):
        """
        Set the marker style based on the passed tuple
        """

        self.marker.markerIndex = \
            Gui.getMarkerIndex(style['shape'], style['size'])

        self.color.rgb = style['color']
