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
Support class for managing Coin3D node styles
"""

from pivy import coin

from ..support.const import Const

class CoinStyles(Const):
    """
    Pre-defined styles for use with Coin3d scenegraph nodes
    """

    class Style():
        """
        Style internal class for CoinStyles class
        """

        def __init__(self, style_id, style=coin.SoDrawStyle.FILLED,
                     shape='default', line_wdith=0.0, point_size=0.0,
                     line_pattern=0xffff, size=9, color=(1.0, 1.0, 1.0),
                     select=True):

            """
            Style constructor
            """
            self.id = style_id
            self.style = style
            self.shape = shape
            self.line_width = line_wdith
            self.point_size = point_size
            self.line_pattern = line_pattern
            self.size = size
            self.color = color
            self.select = select

    DEFAULT = Style('default', color=(0.8, 0.8, 0.8))
    DASHED = Style('dashed', line_pattern=0x0f0f, select=False)
    SELECTED = Style('selected', color=(1.0, 0.9, 0.0))
    ERROR = Style('error', color=(1.0, 0.0, 0.0))
