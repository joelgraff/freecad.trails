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
Style support for Tracker objects
"""

from pivy import coin

from ...coin_style import CoinStyles

class Style():
    """
    Style support for Tracker objects
    """

    #members added by Base
    base_node = None

    def __init__(self):
        """
        Constructor
        """

        if not self.base_node:
            return

        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()

        self.base_node.addChild(self.draw_style)
        self.base_node.addChild(self.color)

        self.coin_style = CoinStyles.DEFAULT
        self.active_style = None

        super().__init__()

    def set_style(self, style=None, draw=None, color=None):
        """
        Update the tracker style
        """

        if self.active_style == style:
            return

        if not draw:
            draw = self.draw_style

        if not color:
            color = self.color

        if not style:
            style = self.coin_style

        draw.lineWidth = style.line_width
        draw.style = style.style
        draw.linePattern = style.line_pattern

        color.rgb = style.color

        self.active_style = style
