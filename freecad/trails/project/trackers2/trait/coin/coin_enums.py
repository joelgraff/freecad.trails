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
Coin-based enumerations
"""

from pivy import coin
from ...support.const import Const

class MouseEvents(Const):
    """
    Mouse state event constant enumerants
    """
    LOCATION2 = coin.SoLocation2Event.getClassTypeId()
    MOUSE_BUTTON = coin.SoMouseButtonEvent.getClassTypeId()

class PickStyles(Const):
    """
    SoPickStyle enumerants
    """

    UNPICKABLE = coin.SoPickStyle.UNPICKABLE
    SHAPE = coin.SoPickStyle.SHAPE
    BOX = coin.SoPickStyle.BOUNDING_BOX
    SHAPE_ON_TOP = coin.SoPickStyle.SHAPE_ON_TOP
    BOX_ON_TOP = coin.SoPickStyle.BOUNDING_BOX_ON_TOP
    FACES = coin.SoPickStyle.SHAPE_FRONTFACES

class CoinNodes(Const):
    """
    Const class of enumerants correlating to coin node types
    """

    COLOR = coin.SoBaseColor
    COORDINATE = coin.SoCoordinate3
    DRAW_STYLE = coin.SoDrawStyle
    EVENT_CB = coin.SoEventCallback
    GROUP = coin.SoGroup
    LINE_SET = coin.SoLineSet
    MARKER_SET = coin.SoMarkerSet
    PICK_STYLE = coin.SoPickStyle
    SWITCH = coin.SoSwitch
    SEPARATOR = coin.SoSeparator
    TRANSFORM = coin.SoTransform
