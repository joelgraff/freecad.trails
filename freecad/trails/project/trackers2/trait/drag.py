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
Drag traits for Tracker objects
"""

from .base import Base
from .style import Style
from .geometry import Geometry
from .coin.coin_enums import NodeTypes as Nodes
from .coin.coin_styles import CoinStyles
from .coin.coin_group import CoinGroup

class Drag():
    """
    Drag traits for tracker classes
    """

    #Prototypes
    base = None

    #must be defined in the tracker object
    drag_tracker = None

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        #build node structure for the drag nodes
        self.drag = CoinGroup(
            is_separator=True, is_switched=True,
            parent=self.base, name=self.name + '__DRAG'
        )

        self.drag.transform = self.drag.add_node(Nodes.TRANSFORM)

        self.set_style(CoinStyles.DEFAULT)

        #self.base_path_node = self.marker_node

        self.base.set_visibility(True)

    def set_as_global(self):
        """
        Set the current tracker's drag tracker as the global tracker
        """

        self.global_tracker = self.drag_tracker