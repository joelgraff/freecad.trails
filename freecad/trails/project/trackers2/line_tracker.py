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

from .trait.coin.coin_styles import CoinStyles
from .geometry_tracker import GeometryTracker

class LineTracker(GeometryTracker):
    """
    Tracker object for SoLineSet
    """

    def __init__(self, name, points, parent):
        """
        Constructor
        """

        super().__init__(name=name, parent=parent)

        #build node structure for the node tracker
        self.add_line_set('LINE_SET')

        self.set_style(CoinStyles.DEFAULT)

        #self.base_path_node = self.line_node

        self.set_visibility(True)
        self.update(points)
