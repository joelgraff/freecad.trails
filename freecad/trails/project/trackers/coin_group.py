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
Support class for managing Coin3D SoGroup nodes
"""
from pivy import coin

class CoinGroup():
    """
    Local class to facilitate tracking nodes in groups
    """

    def __init__(self, id, no_marker=False):
        """
        Constructor
        """

        self.group = coin.SoGroup()
        self.coord = coin.SoCoordinate3()
        self.marker = coin.SoMarkerSet()
        self.line = coin.SoLineSet()

        self.group.addChild(self.coord)

        if not no_marker:
            self.group.addChild(self.marker)

        self.group.addChild(self.line)

        self.group.setName(id)

    def set_coordinates(self, coords):
        """
        Set the coordinate node values
        """

        _count = len(coords)

        self.coord.point.setNum(_count)
        self.coord.point.setValues(0, _count, [list(_v) for _v in coords])

        self.line.numVertices.setValue(_count)