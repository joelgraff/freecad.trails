# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2018 Joel Graff <monograff76@gmail.com>               *
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
Picking traits for trackers
"""

from .coin.coin_enums import NodeTypes as Nodes
from .coin.coin_enums import PickStyles as Styles

class Pick():
    """
    Picking traits for trackers
    """

    #Base prototype
    base = None

    def __init__(self):
        """
        Constructor
        """

        self.picker = self.base.add_node(Nodes.PICK_STYLE, 'Pick_Style')

    def set_pick_style(self, is_pickable):
        """
        Set the selectability of the node using the SoPickStyle node
        """

        _state = Styles.UNPICKABLE

        if is_pickable:
            _state = Styles.SHAPE

        self.picker.style.setValue(_state)

    def is_pickable(self):
        """
        Return a bool indicating whether or not the node may be selected
        """

        return self.picker.style.getValue() != Styles.UNPICKABLE
