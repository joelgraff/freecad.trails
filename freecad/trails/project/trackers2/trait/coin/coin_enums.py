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

class NodeTypes(Const):
    """
    Const class of enumerants correlating to coin node types
    """

    NODE = coin.SoNode
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

class MarkerStyles(Const):
    """
    Const class of enumerants for coin SoMarkerSet.SoMarkerType
    """

    NONE = coin.SoMarkerSet.NONE

    #size 5
    CROSS_5 = coin.SoMarkerSet.CROSS_5_5
    PLUS_5 = coin.SoMarkerSet.PLUS_5_5
    MINUS_5 = coin.SoMarkerSet.MINUS_5_5
    SLASH_5 = coin.SoMarkerSet.SLASH_5_5
    BACKSLASH_5 = coin.SoMarkerSet.BACKSLASH_5_5
    BAR_5 = coin.SoMarkerSet.BAR_5_5
    STAR_5 = coin.SoMarkerSet.STAR_5_5
    Y_5 = coin.SoMarkerSet.Y_5_5
    LIGHTNING_5 = coin.SoMarkerSet.LIGHTNING_5_5
    WELL_5 = coin.SoMarkerSet.WELL_5_5
    CIRCLE_LINE_5 = coin.SoMarkerSet.CIRCLE_LINE_5_5
    SQUARE_LINE_5 = coin.SoMarkerSet.SQUARE_LINE_5_5
    DIAMOND_LINE_5 = coin.SoMarkerSet.DIAMOND_LINE_5_5
    TRIANGLE_LINE_5 = coin.SoMarkerSet.TRIANGLE_LINE_5_5
    RHOMBUS_LINE_5 = coin.SoMarkerSet.RHOMBUS_LINE_5_5
    HOURGLASS_LINE_5 = coin.SoMarkerSet.HOURGLASS_LINE_5_5
    SATELLITE_LINE_5 = coin.SoMarkerSet.SATELLITE_LINE_5_5
    PINE_TREE_LINE_5 = coin.SoMarkerSet.PINE_TREE_LINE_5_5
    CAUTION_LINE_5 = coin.SoMarkerSet.CAUTION_LINE_5_5
    SHIP_LINE_5 = coin.SoMarkerSet.SHIP_LINE_5_5
    CIRCLE_FILLED_5 = coin.SoMarkerSet.CIRCLE_FILLED_5_5
    SQUARE_FILLED_5 = coin.SoMarkerSet.SQUARE_FILLED_5_5
    DIAMOND_FILLED_5 = coin.SoMarkerSet.DIAMOND_FILLED_5_5
    TRIANGLE_FILLED_5 = coin.SoMarkerSet.TRIANGLE_FILLED_5_5
    RHOMBUS_FILLED_5 = coin.SoMarkerSet.RHOMBUS_FILLED_5_5
    HOURGLASS_FILLED_5 = coin.SoMarkerSet.HOURGLASS_FILLED_5_5
    SATELLITE_FILLED_5 = coin.SoMarkerSet.SATELLITE_FILLED_5_5
    PINE_TREE_FILLED_5 = coin.SoMarkerSet.PINE_TREE_FILLED_5_5
    CAUTION_FILLED_5 = coin.SoMarkerSet.CAUTION_FILLED_5_5
    SHIP_FILLED_5 = coin.SoMarkerSet.SHIP_FILLED_5_5

    #size 7
    CROSS_7 = coin.SoMarkerSet.CROSS_7_7
    PLUS_7 = coin.SoMarkerSet.PLUS_7_7
    MINUS_7 = coin.SoMarkerSet.MINUS_7_7
    SLASH_7 = coin.SoMarkerSet.SLASH_7_7
    BACKSLASH_7 = coin.SoMarkerSet.BACKSLASH_7_7
    BAR_7 = coin.SoMarkerSet.BAR_7_7
    STAR_7 = coin.SoMarkerSet.STAR_7_7
    Y_7 = coin.SoMarkerSet.Y_7_7
    LIGHTNING_7 = coin.SoMarkerSet.LIGHTNING_7_7
    WELL_7 = coin.SoMarkerSet.WELL_7_7
    CIRCLE_LINE_7 = coin.SoMarkerSet.CIRCLE_LINE_7_7
    SQUARE_LINE_7 = coin.SoMarkerSet.SQUARE_LINE_7_7
    DIAMOND_LINE_7 = coin.SoMarkerSet.DIAMOND_LINE_7_7
    TRIANGLE_LINE_7 = coin.SoMarkerSet.TRIANGLE_LINE_7_7
    RHOMBUS_LINE_7 = coin.SoMarkerSet.RHOMBUS_LINE_7_7
    HOURGLASS_LINE_7 = coin.SoMarkerSet.HOURGLASS_LINE_7_7
    SATELLITE_LINE_7 = coin.SoMarkerSet.SATELLITE_LINE_7_7
    PINE_TREE_LINE_7 = coin.SoMarkerSet.PINE_TREE_LINE_7_7
    CAUTION_LINE_7 = coin.SoMarkerSet.CAUTION_LINE_7_7
    SHIP_LINE_7 = coin.SoMarkerSet.SHIP_LINE_7_7
    CIRCLE_FILLED_7 = coin.SoMarkerSet.CIRCLE_FILLED_7_7
    SQUARE_FILLED_7 = coin.SoMarkerSet.SQUARE_FILLED_7_7
    DIAMOND_FILLED_7 = coin.SoMarkerSet.DIAMOND_FILLED_7_7
    TRIANGLE_FILLED_7 = coin.SoMarkerSet.TRIANGLE_FILLED_7_7
    RHOMBUS_FILLED_7 = coin.SoMarkerSet.RHOMBUS_FILLED_7_7
    HOURGLASS_FILLED_7 = coin.SoMarkerSet.HOURGLASS_FILLED_7_7
    SATELLITE_FILLED_7 = coin.SoMarkerSet.SATELLITE_FILLED_7_7
    PINE_TREE_FILLED_7 = coin.SoMarkerSet.PINE_TREE_FILLED_7_7
    CAUTION_FILLED_7 = coin.SoMarkerSet.CAUTION_FILLED_7_7
    SHIP_FILLED_7 = coin.SoMarkerSet.SHIP_FILLED_7_7

    #size 9
    CROSS_9 = coin.SoMarkerSet.CROSS_9_9
    PLUS_9 = coin.SoMarkerSet.PLUS_9_9
    MINUS_9 = coin.SoMarkerSet.MINUS_9_9
    SLASH_9 = coin.SoMarkerSet.SLASH_9_9
    BACKSLASH_9 = coin.SoMarkerSet.BACKSLASH_9_9
    BAR_9 = coin.SoMarkerSet.BAR_9_9
    STAR_9 = coin.SoMarkerSet.STAR_9_9
    Y_9 = coin.SoMarkerSet.Y_9_9
    LIGHTNING_9 = coin.SoMarkerSet.LIGHTNING_9_9
    WELL_9 = coin.SoMarkerSet.WELL_9_9
    CIRCLE_LINE_9 = coin.SoMarkerSet.CIRCLE_LINE_9_9
    SQUARE_LINE_9 = coin.SoMarkerSet.SQUARE_LINE_9_9
    DIAMOND_LINE_9 = coin.SoMarkerSet.DIAMOND_LINE_9_9
    TRIANGLE_LINE_9 = coin.SoMarkerSet.TRIANGLE_LINE_9_9
    RHOMBUS_LINE_9 = coin.SoMarkerSet.RHOMBUS_LINE_9_9
    HOURGLASS_LINE_9 = coin.SoMarkerSet.HOURGLASS_LINE_9_9
    SATELLITE_LINE_9 = coin.SoMarkerSet.SATELLITE_LINE_9_9
    PINE_TREE_LINE_9 = coin.SoMarkerSet.PINE_TREE_LINE_9_9
    CAUTION_LINE_9 = coin.SoMarkerSet.CAUTION_LINE_9_9
    SHIP_LINE_9 = coin.SoMarkerSet.SHIP_LINE_9_9
    CIRCLE_FILLED_9 = coin.SoMarkerSet.CIRCLE_FILLED_9_9
    SQUARE_FILLED_9 = coin.SoMarkerSet.SQUARE_FILLED_9_9
    DIAMOND_FILLED_9 = coin.SoMarkerSet.DIAMOND_FILLED_9_9
    TRIANGLE_FILLED_9 = coin.SoMarkerSet.TRIANGLE_FILLED_9_9
    RHOMBUS_FILLED_9 = coin.SoMarkerSet.RHOMBUS_FILLED_9_9
    HOURGLASS_FILLED_9 = coin.SoMarkerSet.HOURGLASS_FILLED_9_9
    SATELLITE_FILLED_9 = coin.SoMarkerSet.SATELLITE_FILLED_9_9
    PINE_TREE_FILLED_9 = coin.SoMarkerSet.PINE_TREE_FILLED_9_9
    CAUTION_FILLED_9 = coin.SoMarkerSet.CAUTION_FILLED_9_9
    SHIP_FILLED_9 = coin.SoMarkerSet.SHIP_FILLED_9_9

    #no @staticmethod decorator or self argument for Const object methods
    def get(shape, size):
        """
        Convenience function to get marker index using shape / size arguments
        """
        #pylint: disable=no-self-argument

        return MarkerStyles.__dict__.get(shape.upper() + '_' + str(size))

    def get_by_value(value):
        """
        Return the marker name using the markerIndex value
        """
        #pylint: disable=no-self-argument

        if isinstance(value, coin.SoMFInt32):
            value = value.getValues()[0]

        _vals = list(MarkerStyles.__dict__.values())
        _keys = list(MarkerStyles.__dict__.keys())

        if value in _vals:
            return _keys[_vals.index(value)]

        return ''
