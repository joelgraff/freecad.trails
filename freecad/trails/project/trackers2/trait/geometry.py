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
Geometry nodes for Tracker objects
"""

from ..support.smart_tuple import SmartTuple

from .coin.coin_group import CoinGroup
from .coin.coin_enums import NodeTypes as Nodes

class Geometry():
    """
    Geometry nodes for Tracker objects
    """

    #members provided by Base, Style
    base = None
    active_style = None
    name = ''

    def set_visibility(self, visible=True): """prototype"""; pass

    def __init__(self):
        """
        Constructor
        """

        if not (self.active_style and self.base):
            return

        self.geometry = CoinGroup(
            is_separator=False, is_switched=False,
            parent=self.base, name=self.name + '__GEOMETRY')

        self.geometry.transform = self.geometry.add_node(Nodes.TRANSFORM)
        self.geometry.coordinate = self.geometry.add_node(Nodes.COORDINATE)

        self.last_coordinates = []

        super().__init__()

    def update(self, coordinates):
        """
        Update implementation
        """

        self.last_coordinates = self.set_coordinates(coordinates)

    def set_coordinates(self, coordinates=None):
        """
        Update the SoCoordinate3 with the passed coordinates
        Assumes coordinates is a list of 3-float tuples
        """

        if not coordinates:
            return

        #encapsulate a single coordinate as a list
        if not isinstance(coordinates, list):
            coordinates = [coordinates]

        #ensure coordinate points are tuples
        coordinates = [SmartTuple(_v)._tuple for _v in coordinates]

        self.geometry.coordinate.point.setValues(coordinates)

        return coordinates

    def get(self, _dtype=tuple):
        """
        Return the coordinates as the specified iterable type
        """

        return [
            _dtype(_v.getValue()) \
                for _v in self.geometry.coordinate.point.getValues()
        ]
