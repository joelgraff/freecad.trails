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
Line tracker class for tracker objects
"""

from .base import Base
from .style import Style
from .select import Select
from .geometry import Geometry
from .coin_styles import CoinStyles
from .coin_enums import CoinNodes as Nodes

class LineTracker(Base, Style, Select, Geometry):
    """
    Tracker object for SoLineSet
    """

    def __init__(self, name, points):
        """
        Constructor
        """

        super().__init__(name=name)

        #build node structure for the node tracker
        self.line_set =\
            self.geometry.add_node(Nodes.LINE_SET, self.name + 'LINE')

        self.set_style(CoinStyles.DEFAULT)

        #self.base_path_node = self.line_node

        self.base.set_visibility(True)
        self.update(points)

    def update(self, coord=None):
        """
        Update the coordinate position
        """
        #PyLint ignore as coordinate argument is optional here
        #pylint: disable=arguments-differ

        Geometry.set_coordinates(self, coord)

    def set_style(self, style=None, draw=None, color=None):
        """
        Override style implementation
        """

        Style.set_style(self, style, draw, color)

    def finalize(self, node=None, parent=None):
        """
        Cleanup
        """

        super().finalize(self.geometry, parent)
